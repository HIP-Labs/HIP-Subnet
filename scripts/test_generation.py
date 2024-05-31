import hip.validator.text_generator as tg
import hip.validator.image_generator as ig
import hip.validator.captcha_generator as cg
import time

if __name__ == "__main__":
    start_time = int(time.time())
    # Text generation
    text_gen = tg.generate_paragraph()
    print("Time taken for text generation: ", int(time.time()) - start_time)
    start_time = int(time.time())
    randomCaptcha = cg.generate_capcha()
    print("Time taken for captcha generation: ", int(time.time()) - start_time)
    # Image generation
    image_gen = ig.generate_image_task(captcha=randomCaptcha["image"])
    print("Time taken for image generation: ", int(time.time()) - start_time)
