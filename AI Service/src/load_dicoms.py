import math
import numpy as np
import tqdm
import pydicom
from pydicom import dcmread
from pydicom.multival import MultiValue
from pydicom.valuerep import DSfloat
from pydicom.uid import UID
from pydicom.dataset import FileDataset
import os
from functools import partial
import typing as tp
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from enum import Enum
from .constants import *
from collections import defaultdict


class DicomSerieError(Enum):
    EMPTY_SERIE = 0
    PHOTOMETRY = 1
    MODALITY = 2
    ROWS_COLS_UNKNOWN = 3
    DEPTH_ERROR = 4
    NO_FRAME_OF_REFERENCE_UID = 5
    NO_PIXEL_SPACING = 6
    NO_ORDERING = 7
    METADATA_INCONSISTENT = 8
    SLICE_SPACING_INCONSISTENCY = 9
    ROWS_COLS_MISMATCH = 10
    DEPTH_MISMATCH = 11
    NO_SLICE_SPACING = (12,)
    MULTI_FRAME_MULTI_FILES = (13,)
    NO_ERROR = 14


def get_dicom_files_path(
    dataset_path: str,
) -> tp.Tuple[tp.DefaultDict[str, tp.List[str]], tp.List[str]]:
    series_path = dataset_path + "series/"
    directories = os.listdir(series_path)
    series_to_files_dict = defaultdict(list)
    for d in directories:  # no need to check dir it is ok, save runtime
        dicom_files = os.listdir(series_path + d)
        for f in dicom_files:  # no need to check isfile it is ok, save runtime
            series_to_files_dict[d].append(series_path + d + "/" + f)
    return series_to_files_dict, directories


def values_equal(v1, v2, tol=1e-3):
    """Compare DICOM tag values based on type."""
    if isinstance(v1, (MultiValue, list)) and isinstance(v2, (MultiValue, list)):
        if len(v1) != len(v2):
            return False
        for a, b in zip(v1, v2):
            if isinstance(a, float) or isinstance(b, float):
                if not math.isclose(float(a), float(b), abs_tol=tol):
                    return False
            else:
                if a != b:
                    return False
        return True
    elif isinstance(v1, (float, DSfloat)) or isinstance(v2, (float, DSfloat)):
        return math.isclose(float(v1), float(v2), abs_tol=tol)
    elif isinstance(v1, UID) or isinstance(v2, UID):
        return str(v1) == str(v2)
    else:
        return v1 == v2


def check_metadata_consistency(dcm0: FileDataset, dcmi: FileDataset) -> bool:
    is_data_consistent = True
    for tag in CONSISTENCY_TAGS:
        is_data_consistent = is_data_consistent and (
            values_equal(dcm0.get(tag, "N/A"), dcmi.get(tag, "N/A"))
        )
        if not is_data_consistent:
            return is_data_consistent
    return is_data_consistent


def check_tags_exist(dcm: FileDataset, tag: str) -> bool:
    if dcm.get(tag, "N/A") == "N/A":
        return False
    return True


def resample_dicom_volume_constant_spacing(
    volume: np.ndarray,
    original_spacing: tp.List[float],
    target_spacing: tp.List[float] = [0.5, 0.5, 0.5],
    interpolation_order: int = 1,
    keep_xy_spacing: bool = False,
    square_spacing_mode: bool = False,
) -> tp.Tuple[np.ndarray, tp.Tuple[float, ...]]:
    if keep_xy_spacing:
        target_spacing[1] = original_spacing[1]
        target_spacing[2] = original_spacing[2]
    if square_spacing_mode:
        min_spacing = min(original_spacing)
        target_spacing = [min_spacing, min_spacing, min_spacing]
    # Calculate resize factor for each axis
    resize_factor = original_spacing / np.array(target_spacing, dtype=np.float32)
    # Adjust to nearest integer shape to avoid fractional voxel counts
    new_shape = np.round(np.array(volume.shape) * resize_factor).astype(int)
    actual_resize_factor = new_shape / np.array(volume.shape)
    if (actual_resize_factor == 0).any():
        resampled_volume = np.array([])
        actual_spacing = (0, 0, 0)
    else:
        actual_spacing = original_spacing / actual_resize_factor
        # Perform resampling
        resampled_volume = ndimage.zoom(
            volume,
            zoom=actual_resize_factor,
            order=interpolation_order,
            mode="nearest",  # for out of bounds filling mode
        )
    return resampled_volume, tuple(actual_spacing)


def resample_dicom_volume_non_constant_spacing(
    volume: np.ndarray,
    z_positions: np.ndarray,
    spacing_xy: tp.List[float],
    target_spacing: tp.List[float] = [0.5, 0.5, 0.5],
    interpolation_order: str = "linear",
    keep_xy_spacing: bool = False,
    square_spacing_mode: bool = False,
) -> np.ndarray:
    diff = np.diff(z_positions)
    assert np.all(diff > 0)
    if keep_xy_spacing:
        target_spacing[1] = spacing_xy[0]
        target_spacing[2] = spacing_xy[1]
    if square_spacing_mode:
        min_spacing = min(spacing_xy)
        target_spacing = [min_spacing, min_spacing, min_spacing]
    # Original coordinates
    z_old = z_positions
    x_old = np.arange(volume.shape[1]) * spacing_xy[0]
    y_old = np.arange(volume.shape[2]) * spacing_xy[1]
    # Interpolator
    interpolator = RegularGridInterpolator(
        (z_old, x_old, y_old),
        volume,
        method=interpolation_order,
        bounds_error=False,  # Return error is boundaries are met
        fill_value=0.0,
    )
    z_new = np.arange(np.min(z_positions), np.max(z_positions), target_spacing[0])
    x_new = np.arange(0, volume.shape[1] * spacing_xy[0], target_spacing[1])
    y_new = np.arange(0, volume.shape[2] * spacing_xy[1], target_spacing[2])
    # Create meshgrid for new coordinates
    zz, xx, yy = np.meshgrid(z_new, x_new, y_new, indexing="ij")
    points = np.column_stack((zz.ravel(), xx.ravel(), yy.ravel()))
    # Resample
    vol_resampled = interpolator(points).reshape(len(z_new), len(x_new), len(y_new))
    return vol_resampled



def load_dicom_serie(
    serie_instance_uid: str,
    dicom_file_list: tp.List[str],
    target_spacing: tp.List[float] = [0.5, 0.5, 0.5],
    load_data: bool = False,
    mean_std_norm: bool = False,
    save_to_npy: bool = False,
    output_path: str = "out/output_volumes/",
    resample: bool = False,
) -> tp.Union[
    tp.Tuple[str, DicomSerieError],
    tp.Tuple[str, DicomSerieError, np.ndarray, np.ndarray, str, np.ndarray],
]:

    error = DicomSerieError.NO_ERROR
    # Check if we have more than 1 dicom file
    if len(dicom_file_list) < 1:
        return serie_instance_uid, DicomSerieError.EMPTY_SERIE
    # Get information from first slide and check data consistency from it
    file0 = pydicom.dcmread(dicom_file_list[0])
    # Check that PhotometricInterpretation is always  MONOCHROME2
    photom = file0.get("PhotometricInterpretation", "N/A")
    if photom != "MONOCHROME2":
        return serie_instance_uid, DicomSerieError.PHOTOMETRY
    # Check that modality is always CT or MR
    modality = file0.get("Modality", "N/A")
    if modality != "CT" and modality != "MR":
        return serie_instance_uid, DicomSerieError.MODALITY

    # Check that depth field is 1
    depth = 0
    multi_frame = False
    if len(file0.pixel_array.shape) == 3:
        multi_frame = True
    elif len(file0.pixel_array.shape) > 3:
        return serie_instance_uid, DicomSerieError.DEPTH_ERROR

    # Check for non empty Rows and Columns fields
    rows = file0.get("Rows", "N/A")
    cols = file0.get("Columns", "N/A")
    if rows == "N/A" or cols == "N/A":
        return serie_instance_uid, DicomSerieError.ROWS_COLS_UNKNOWN
    rows = int(rows)
    cols = int(cols)

    # Check that we have a FrameOfReferenceUID
    # frame_uid = file0.get("FrameOfReferenceUID", "N/A")
    # if frame_uid == "N/A" and not multi_frame:
    #    return serie_instance_uid, DicomSerieError.NO_FRAME_OF_REFERENCE_UID

    # Check that we have PixelSpacing
    pixel_spacing = file0.get("PixelSpacing", "N/A")
    if pixel_spacing == "N/A":
        pixel_spacing = [0.5, 0.5]
        print("WARNING NO_PIXEL_SPACING, taking 0.5mm by default " + serie_instance_uid)
    else:
        pixel_spacing = list(map(float, pixel_spacing))

    # Get DICOM files
    files = []
    # Check that those tags exists for every DICOM file
    position_tag_exists = True
    orientation_tag_exists = True
    instance_uid_tag_exists = True
    spacing_btwn_slices_tag_exists = True
    for f in dicom_file_list:
        file = pydicom.dcmread(f)
        position_tag_exists = position_tag_exists and check_tags_exist(
            file, "ImagePositionPatient"
        )
        orientation_tag_exists = orientation_tag_exists and check_tags_exist(
            file, "ImageOrientationPatient"
        )
        instance_uid_tag_exists = instance_uid_tag_exists and check_tags_exist(
            file, "InstanceNumber"
        )
        spacing_btwn_slices_tag_exists = (
            spacing_btwn_slices_tag_exists
            and check_tags_exist(file, "SpacingBetweenSlices")
        )
        # Check that CONSISTENCY_TAGS are the same between the files
        if not check_metadata_consistency(file0, file):
            error = DicomSerieError.METADATA_INCONSISTENT

        files.append(file)
    if multi_frame and len(files) > 1:
        return serie_instance_uid, DicomSerieError.MULTI_FRAME_MULTI_FILES
    # Check that we have enough info to reorder 2d slices into volume for non multi_frame slices
    if not position_tag_exists and not instance_uid_tag_exists and not multi_frame:
        return serie_instance_uid, DicomSerieError.NO_ORDERING

    # Reorder data to create volume
    z_positions = []
    if position_tag_exists and not multi_frame:
        z_positions = [float(f.ImagePositionPatient[2]) for f in files]
        z_positions.sort(key=lambda x: float(x))
        z_positions = np.array(z_positions)
        files.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        slice_spacing = np.abs(z_positions[1] - z_positions[0])
    elif instance_uid_tag_exists and not multi_frame:
        files.sort(key=lambda x: float(x.InstanceNumber))
        slice_spacing = 0.0
    elif multi_frame:
        slice_spacing = 0.0

    if abs(slice_spacing) < 1e-4 or len(z_positions) == 0:
        slice_spacing = file0.get("SpacingBetweenSlices", "N/A")
        if slice_spacing == "N/A":
            slice_spacing = 0.5
            print(
                "WARNING NO_SLICE_SPACING, taking 0.5mm by default" + serie_instance_uid
            )
        slice_spacing = float(slice_spacing)
        z_positions = np.arange(len(files)) * slice_spacing

    for i in range(0, len(files)):
        # Check if z spacing is consitent across all slides
        if i > 1:
            sp = np.abs(z_positions[i] - z_positions[i - 1])
            if abs(sp - slice_spacing) > 1e-4:
                error = DicomSerieError.SLICE_SPACING_INCONSISTENCY

        # Check if rows and cols spacing are consitent across all slides
        current_rows = files[i].pixel_array.shape[0]
        current_cols = files[i].pixel_array.shape[1]
        if multi_frame:
            current_depth = files[i].pixel_array.shape[0]
            current_rows = files[i].pixel_array.shape[1]
            current_cols = files[i].pixel_array.shape[2]
        if current_rows != rows or current_cols != cols:
            return serie_instance_uid, DicomSerieError.ROWS_COLS_MISMATCH
    # Now process and load data
    if load_data:
        assert (
            error == DicomSerieError.NO_ERROR
            or error == DicomSerieError.SLICE_SPACING_INCONSISTENCY
            or error == DicomSerieError.METADATA_INCONSISTENT
        ), (error + " " + serie_instance_uid)
        # Stack 2d frames on first axis
        if not multi_frame:
            volume = np.stack([f.pixel_array.astype(np.float32) for f in files])
        else:
            volume = files[0].pixel_array.astype(np.float32)
        assert volume.size > 0, "empty volume " + serie_instance_uid
        assert not np.isnan(volume).any(), "volume has nans " + serie_instance_uid

        # Get spacing between slices in the z direction
        # Different from slice_thickness (ex if slice_spacing < slice_thickness the slices are overlaping)
        # More info on https://stackoverflow.com/questions/76149834/dicom-slice-thickness-in-python
        spacing = np.array([slice_spacing] + pixel_spacing)
        # For CT scans convert raw pixel values to Hounsfield units if needed
        if (
            files[0].Modality == "CT"
            and ("RescaleSlope" in files[0])
            and ("RescaleIntercept" in files[0])
        ):
            intercept = float(files[0].RescaleIntercept)
            slope = float(files[0].RescaleSlope)
            volume = volume * slope + intercept
        if resample:
            # Resample volume
            if error == DicomSerieError.NO_ERROR:
                rvolume, rspacing = resample_dicom_volume_constant_spacing(
                    volume, spacing, target_spacing=target_spacing
                )
            elif error == DicomSerieError.SLICE_SPACING_INCONSISTENCY:
                rvolume = resample_dicom_volume_non_constant_spacing(
                    volume, z_positions, pixel_spacing, target_spacing=target_spacing
                )
                rspacing = target_spacing
            if rvolume.size < 1:
                print("WARNING no resampled done otherwise volume is empty")
            else:
                volume = rvolume
                spacing = rspacing
            assert volume.size > 0, "empty volume after resample " + serie_instance_uid
            assert not np.isnan(volume).any(), (
                "volume has nans after resample " + serie_instance_uid
            )

        # Clip outliers and normalize data
        if files[0].Modality == "CT":
            MIN_CT = -1024
            MAX_CT = 3071
            max_val = np.max(volume)
            min_val = np.min(volume)
            if ((min_val < MIN_CT) and (max_val < MIN_CT)) or (
                (min_val > MAX_CT) and (max_val > MAX_CT)
            ):
                print("WARNING min_val max_val scale problem")
            else:
                volume = np.clip(
                    volume, MIN_CT, MAX_CT
                )  # keep air to dense bone, clip outliers
        elif files[0].Modality == "MR":
            min_outlier = np.percentile(volume, 1)
            max_outlier = np.percentile(volume, 99)
            if np.abs(min_outlier - max_outlier) > 1e-2:
                volume = np.clip(volume, min_outlier, max_outlier)  # clip outliers
            else:
                print("WARNING min_outlier max_outlier are the same")
        else:
            assert False, "Modality is neither CT nor MR " + serie_instance_uid

        if mean_std_norm:
            mean = np.mean(volume)
            stdev = np.std(volume)
            volume = (volume - mean) / stdev  # z score normalization
        else:
            max_val = np.max(volume)
            min_val = np.min(volume)
            if np.abs(max_val - min_val) < 1e-2:
                assert False, "min and max are the same " + serie_instance_uid
            volume = (volume - min_val) / (max_val - min_val)  # min max normalization
            assert (np.max(volume) - 1.0) < 1e-5, (
                np.max(volume) + " " + serie_instance_uid
            )
            assert np.min(volume) < 1e-5, np.min(volume) + " " + serie_instance_uid
        # volume = crop_or_pad(volume)
        volume2 = np.transpose(volume, (2, 0, 1))  # Permute axes to get coronal view
        volume3 = np.transpose(volume, (1, 0, 2))  # Permute axes to get sagittal view
        if save_to_npy:
            np.savez_compressed(
                output_path + serie_instance_uid + "_volume.npz", volume
            )
            # np.save(output_path + serie_instance_uid + "_volume2.npy", volume)
            # np.save(output_path + serie_instance_uid + "_volume3.npy", volume)
            np.savez_compressed(
                output_path + serie_instance_uid + "_spacing.npz", spacing
            )
            np.savez_compressed(
                output_path + serie_instance_uid + "_modality.npz",
                np.array(files[0].Modality == "CT"),
            )
        return (
            serie_instance_uid,
            error,
            volume,
            volume2,
            volume3,
            spacing,
            np.array(files[0].Modality == "CT"),
            z_positions,
        )
    return serie_instance_uid, error


def load_dicom_series(
    serie_instance_uid: str,
    series_to_files_dict: tp.Dict[str, tp.List[str]],
    target_spacing: tp.List[float] = [0.5, 0.5, 0.5],
    load_data: bool = False,
    mean_std_norm: bool = False,
    save_to_npy: bool = False,
    output_path: str = "out/output_volumes/",
    resample: bool = False,
) -> tp.Union[
    tp.Tuple[str, DicomSerieError],
    tp.Tuple[str, DicomSerieError, np.ndarray, np.ndarray, str, np.ndarray],
]:
    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    # Extract list dicom file path that corresponds to  serie_instance_uid
    dicom_file_list = series_to_files_dict[serie_instance_uid]
    return load_dicom_serie(
        serie_instance_uid,
        dicom_file_list,
        target_spacing,
        load_data,
        mean_std_norm,
        save_to_npy,
        output_path,
        resample,
    )


def load_from_npz(
    serie_instance_uid: str,
    output_path: str = "out/output_volumes/",
) -> tp.Tuple[np.ndarray, np.ndarray, str, np.ndarray]:
    volume = np.load(output_path + serie_instance_uid + "_volume.npz")
    volume = list(volume.values())[0]
    assert np.min(volume) >= -1e-3, np.min(volume)
    assert np.max(volume) <= (1.0 + 1e-3), np.max(volume)

    spacing = np.load(output_path + serie_instance_uid + "_spacing.npz")
    modality = np.load(output_path + serie_instance_uid + "_modality.npz")
    return (
        volume,
        list(spacing.values())[0],
        list(modality.values())[0],
    )
