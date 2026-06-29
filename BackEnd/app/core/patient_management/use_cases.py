from typing import List, Optional
import asyncio
from app.core.patient_management.entities import AneurysmAnalysisResult, Patient
from app.core.patient_management.repositories import Patients
from app.core.patient_management.services import ScanAnalyzer
from app.modules.system_settings.repositories import SettingsRepository
from app.core.patient_management.services import Notifier

class GetAllPatients:
    def __init__(self, patient_repo: Patients, settings_repo: SettingsRepository):
        self.patient_repo = patient_repo
        self.settings_repo = settings_repo

    async def execute(self) -> List[Patient] | None:
        patients = await self.patient_repo.get_all()
        return patients


class GetPatientDiagnosticReport:
    def __init__(self, patient_repo: Patients):
        self.patient_repo = patient_repo

    async def execute(self, patient_id: str) -> Optional[Patient]:
        if not patient_id:
            return None
        patient = await self.patient_repo.get_patient_by_id(patient_id)
        if not patient:
            return None
        return patient

class DetectAneurysmProbabilities:
    def __init__(
            self, 
            patient_repo: Patients,
            ai_service: ScanAnalyzer, 
            notifier: Notifier,
            settings_repo : SettingsRepository
            ):
        self.patient_repo = patient_repo
        self.ai_service = ai_service
        self.notifier = notifier
        self.settings_repo = settings_repo
        

    async def execute(
                self,
                scan_id: str,
                include_heatmap: bool = False,
                target_label: str = "Aneurysm Present"
            ) -> AneurysmAnalysisResult:
        binary_data = await self.patient_repo.get_scan_file(scan_id)
        if not binary_data:
            raise ValueError(f"Scan record with id {scan_id} not found in DB")

        analysis_results = await self.ai_service.analyze_scan(
            scan_id= scan_id,
            binary_data= binary_data,
            explain= include_heatmap,
            target_label= target_label
        )
        
        await self.patient_repo.update_scan_results(
            scan_id=scan_id,
            ai_results=analysis_results,
        )

        system_settings = await self.settings_repo.get_settings()
        high_risk_threshold = system_settings.aneurysm_high_risk_threshold if system_settings else 0.7
        overall_prob = analysis_results.overall.probability if analysis_results.overall else 0.0

        if overall_prob >= high_risk_threshold:
            asyncio.create_task(self.notifier.send_urgent_alert(scan_id=scan_id, probability=overall_prob))

        return analysis_results

class GetSliceImage:
    def __init__(self,patient_repo: Patients):
        self.patient_repo = patient_repo
    
    async def execute(self, image_ref: str)->Optional[bytes]:
        """ Fetches a stored overlay or raw slice image by its reference"""
        return await self.patient_repo.get_slice_image(image_ref)