from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
import torch

pipeline = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
).to("cuda")


def generate_image(prompt):
    image = pipeline(prompt=prompt, guidance_scale=0.0, num_inference_steps=1).images[0]
    return image


if __name__ == "__main__":
    prompt = "A beautiful sunset over the ocean"
    image = generate_image(prompt)
    image.save("image.png")
    print("Image saved as image.png")
