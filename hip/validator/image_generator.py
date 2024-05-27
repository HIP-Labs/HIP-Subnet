from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
import torch
from hip.validator import text_generator

pipeline = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
).to("cuda:1")


def generate_image(prompt):
    image = pipeline(prompt=prompt, guidance_scale=0.0, num_inference_steps=1).images[0]
    return image


if __name__ == "__main__":
    prompt = text_generator.generate_caption()
    print("Prompt:", prompt)
    image = generate_image(prompt)
    image.save("test.png")
    print("Image saved as test.png")
