# GeoSense Agent — Phase 2: Deep Learning Image Classification

## 1. Overview

Phase 2 implements a deep-learning satellite image segmentation and classification pipeline for the GeoSense Agent project.

The workflow uses Sentinel-2 imagery, six spectral bands, a U-Net semantic segmentation model, validation metrics, and a reusable image_classifier.py inference module.

The supplied temporal dataset contains imagery from 2020 and 2025.

## 2. Objectives

- Prepare Sentinel-2 image chips for deep learning.
- Prepare semantic segmentation labels.
- Train a multi-class U-Net model.
- Evaluate the model using pixel accuracy and IoU.
- Generate segmentation visualizations.
- Develop a reusable image classification module.
- Calculate NDVI and NDWI during inference.
- Implement temporal NDVI-based change detection.
- Prepare Phase 2 outputs for GeoSense Agent integration.

## 3. Dataset

- Total paired chips: 182
- Chip size: 224 × 224 pixels
- Input bands: 6
- Band order: B2, B3, B4, B8, B11, B12

### Dataset split

| Dataset | Samples |
|---|---:|
| Training | 145 |
| Validation | 37 |
| Total | 182 |

### Temporal data

| Year | Chips |
|---|---:|
| 2020 | 91 |
| 2025 | 91 |
| Common chip IDs | 91 |

The supplied dataset contains 2020/2025 imagery. Therefore, temporal change detection was implemented for 2020 → 2025.

## 4. Semantic Classes

| Class ID | Class |
|---:|---|
| 0 | Urban |
| 1 | Vegetation |
| 2 | Water |
| 3 | Bare Land |
| 4 | Agriculture |

## 5. U-Net Model

- Architecture: U-Net
- Encoder: ResNet34
- Input channels: 6
- Output classes: 5
- Parameters: 24,446,357
- Encoder pretrained weights: None

## 6. Training

- Epochs: 30
- Optimizer: AdamW
- Learning rate: 0.0001
- Weight decay: 0.00001
- Scheduler: StepLR
- Step size: 10 epochs
- Gamma: 0.5
- Loss: Weighted Cross Entropy
- Ignore index: 255

Data augmentation:
- Horizontal flip
- Vertical flip
- Random 90-degree rotation

## 7. Training Results

| Metric | Value |
|---|---:|
| Training Loss | 0.4470 |
| Validation Loss | 0.4391 |
| Training Accuracy | 73.39% |
| Validation Accuracy | 75.96% |
| Learning Rate | 0.000025 |

Best validation loss: 0.4391431518503138

Best validation accuracy: 75.96%

## 8. Validation Performance

Evaluation was performed on all 37 validation chips.

Pixel Accuracy: 75.96%

| Class | IoU |
|---|---:|
| Urban | 13.74% |
| Vegetation | 70.64% |
| Water | 80.88% |
| Bare Land | 52.63% |
| Agriculture | 60.19% |
| Mean IoU | 55.61% |

## 9. Confusion Matrix

Validation confusion matrix:

3284 0 0 167 10
56 458201 51 985 75482
6 2 31388 456 2
16774 1132 6552 282120 63347
3610 112772 350 164537 635216

## 10. Validation Outputs

### Segmentation Result

`validation_segmentation_result.png`

### Validation Metrics

`validation_metrics.json`

### Confusion Matrix

![Phase 2 Confusion Matrix](../Phase2_Exercise4/confusion_matrix.png)

## 11. Image Classifier

Module:

Phase2_Exercise5/image_classifier.py

Main function:

classify_imagery(lat, lon, radius_m)

The function returns latitude, longitude, radius, dominant class, class distribution, confidence, NDVI, NDWI, temporal NDVI values, change flag, chip ID, and inference time.

## 12. Spectral Indices

NDVI = (NIR - Red) / (NIR + Red)

Red = B4

NIR = B8

NDWI = (Green - NIR) / (Green + NIR)

Green = B3

NIR = B8

Both indices are constrained to [-1, 1].

## 13. Temporal Change Detection

Corresponding 2020 and 2025 chips are matched using their chip IDs.

Change criterion:

abs(NDVI_2025 - NDVI_2020) > 0.15

The implementation uses mean NDVI for the corresponding image patches.

## 14. Example Inference

Latitude: 22.660003041914926
Longitude: 88.37257455901364
Radius: 500 m

Dominant class: Agriculture
Dominant class ID: 4
Confidence: 0.6945
Mean NDVI: 0.2975
Mean NDWI: -0.3143
2020 NDVI: 0.2938
2025 NDVI: 0.2975
NDVI difference: 0.00376
Change threshold: 0.15
Change flag: False

## 15. Inference Performance

Total inference time: 2.28 seconds

Required: less than 3 seconds

Status: PASS

## 16. Model Loading

The module checks for prithvi_finetuned.pth first.

If unavailable, it falls back to unet_best.pth.

The current verified implementation uses the trained U-Net model.

## 17. Output Files

Phase2_models/
- unet_best.pth
- unet_final.pth
- unet_latest_checkpoint.pth
- unet_history.json

Phase2_Exercise4/
- validation_segmentation_result.png
- validation_metrics.json

Phase2_Exercise5/
- image_classifier.py
- README_Phase2.md

## 18. Limitations

1. The supplied temporal dataset contains 2020 and 2025 imagery.
2. Prithvi fine-tuning was not available, so the trained U-Net checkpoint is used.
3. GPU acceleration was unavailable during final verification.
4. Temporal change detection uses mean NDVI difference.
5. Urban class IoU is lower than the other major classes.

## 19. Final Verification

Model files: PASS
Exercise 4 outputs: PASS
image_classifier.py: PASS
Dataset: PASS
2020 temporal data: PASS
2025 temporal data: PASS
Temporal matching: PASS
NDVI/NDWI computation: PASS
Change detection: PASS
Inference performance: PASS

Final verification: 10/10 checks passed.

## Phase 2 Status

PHASE 2 COMPLETED

The Phase 2 deep-learning segmentation, evaluation, reusable image classifier, and temporal NDVI change-detection pipeline have been implemented and verified.