import numpy as np
import torch
import modules.core as core

from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from transformers import AutoFeatureExtractor
from PIL import Image

safety_model_id = "CompVis/stable-diffusion-safety-checker"
safety_feature_extractor = None
safety_checker = None


def numpy_to_pil(image):
    image = (image * 255).round().astype("uint8")

    #pil_image = Image.fromarray(image, 'RGB')
    pil_image = Image.fromarray(image)

    return pil_image


# check and replace nsfw content
def check_safety(x_image):
    global safety_feature_extractor, safety_checker

    if safety_feature_extractor is None:
        safety_feature_extractor = AutoFeatureExtractor.from_pretrained(safety_model_id)
        safety_checker = StableDiffusionSafetyChecker.from_pretrained(safety_model_id)

    safety_checker_input = safety_feature_extractor(numpy_to_pil(x_image), return_tensors="pt")
    x_checked_image, has_nsfw_concept = safety_checker(images=x_image, clip_input=safety_checker_input.pixel_values)

    return x_checked_image, has_nsfw_concept


def censor_single(x):
    x_checked_image, has_nsfw_concept = check_safety(x)
    print(has_nsfw_concept)
    if has_nsfw_concept[0]:
        imageshape = x_checked_image.shape
        x_checked_image = np.zeros((imageshape[0], imageshape[1], 3), dtype = np.uint8)

    return x_checked_image


def censor_batch(images):
    images = [censor_single(image) for image in images]

    return images