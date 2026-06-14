DICOM_TAG_ALLOWLIST = [
    "BitsAllocated",  # Number of bits allocated for each pixel sample (e.g., 8, 16, 32).
    "BitsStored",  # Number of bits actually used to store pixel data (can be less than BitsAllocated).
    "Columns",  # Number of pixel columns in the image (image width).
    "FrameOfReferenceUID",  # Unique identifier for a spatial reference frame; helps align images.
    "HighBit",  # Position of the most significant bit in the pixel data (zero-based index).
    "ImageOrientationPatient",  # Direction cosines describing the image rows and columns relative to the patient.
    "ImagePositionPatient",  # Coordinates of the top-left voxel (first pixel) in the patient’s 3D space.
    "InstanceNumber",  # Ordinal number of the image in the series (for ordering slices).
    "Modality",  # Imaging modality type (e.g., CT, MR, US, CR, PET).
    "PatientID",  # Identifier for the patient (not necessarily their name — often anonymized).
    "PhotometricInterpretation",  # How pixel values should be interpreted (e.g., MONOCHROME2, RGB).
    "PixelRepresentation",  # Pixel data type: 0 = unsigned integer, 1 = two’s complement signed integer.
    "PixelSpacing",  # Physical spacing between pixels in millimeters (row spacing, column spacing).
    "PlanarConfiguration",  # For color images: indicates whether RGB values are interleaved or planar.
    "RescaleIntercept",  # Value to add to stored pixel values for display (used in CT to get Hounsfield units).
    "RescaleSlope",  # Scaling factor to multiply stored pixel values by (before adding intercept).
    "RescaleType",  # Type of units after rescaling (e.g., HU for Hounsfield units).
    "Rows",  # Number of pixel rows in the image (image height).
    "SOPClassUID",  # Unique identifier of the DICOM object type (e.g., CT Image Storage).
    "SOPInstanceUID",  # Unique identifier for this particular DICOM instance (image).
    "SamplesPerPixel",  # Number of samples (color channels) per pixel (1 for grayscale, 3 for RGB).
    "SliceThickness",  # Physical thickness of the slice in millimeters.
    "SpacingBetweenSlices",  # Distance between the centers of adjacent slices (can differ from SliceThickness).
    "StudyInstanceUID",  # Unique identifier for the entire study (all related series/images).
    "TransferSyntaxUID",  # Specifies the encoding of pixel data (byte order, compression, etc.).
]

TAGS_TO_CHECK = [
    "BitsAllocated",
    "BitsStored",
    "Columns",
    "FrameOfReferenceUID",
    "HighBit",
    "Modality",
    "PhotometricInterpretation",
    "PixelRepresentation",
    "PixelSpacing",
    "PlanarConfiguration",
    "RescaleIntercept",
    "RescaleSlope",
    "RescaleType",
    "Rows",
    "SamplesPerPixel",
    "SliceThickness",
    "SpacingBetweenSlices",
]

CONSISTENCY_TAGS = [
    "Columns",  # Number of pixel columns in the image (image width).
    "FrameOfReferenceUID",  # Unique identifier for a spatial reference frame; helps align images.
    "Modality",  # Imaging modality type (e.g., CT, MR, US, CR, PET).
    "PatientID",  # Identifier for the patient (not necessarily their name — often anonymized).
    "PhotometricInterpretation",  # How pixel values should be interpreted (e.g., MONOCHROME2, RGB).
    "PixelSpacing",  # Physical spacing between pixels in millimeters (row spacing, column spacing).
    "Rows",  # Number of pixel rows in the image (image height).
    "SliceThickness",  # Physical thickness of the slice in millimeters.
    "SpacingBetweenSlices",  # Distance between the centers of adjacent slices (can differ from SliceThickness).
    "StudyInstanceUID",  # Unique identifier for the entire study (all related series/images).
    "ImageOrientationPatient",  # Direction cosines describing the image rows and columns relative to the patient'
]


LABEL_COLS = [
    "Left Infraclinoid Internal Carotid Artery",
    "Right Infraclinoid Internal Carotid Artery",
    "Left Supraclinoid Internal Carotid Artery",
    "Right Supraclinoid Internal Carotid Artery",
    "Left Middle Cerebral Artery",
    "Right Middle Cerebral Artery",
    "Anterior Communicating Artery",
    "Left Anterior Cerebral Artery",
    "Right Anterior Cerebral Artery",
    "Left Posterior Communicating Artery",
    "Right Posterior Communicating Artery",
    "Basilar Tip",
    "Other Posterior Circulation",
    "Aneurysm Present",
]

LABEL_WEIGHTS = {
    "Left Infraclinoid Internal Carotid Artery": 1.0,
    "Right Infraclinoid Internal Carotid Artery": 1.0,
    "Left Supraclinoid Internal Carotid Artery": 1.0,
    "Right Supraclinoid Internal Carotid Artery": 1.0,
    "Left Middle Cerebral Artery": 1.0,
    "Right Middle Cerebral Artery": 1.0,
    "Anterior Communicating Artery": 1.0,
    "Left Anterior Cerebral Artery": 1.0,
    "Right Anterior Cerebral Artery": 1.0,
    "Left Posterior Communicating Artery": 1.0,
    "Right Posterior Communicating Artery": 1.0,
    "Basilar Tip": 1.0,
    "Other Posterior Circulation": 1.0,
    "Aneurysm Present": 13.0,
}
