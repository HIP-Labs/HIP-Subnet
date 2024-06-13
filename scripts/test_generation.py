import hip.validator.text_generator as tg
import hip.validator.generators as task_generators
import time

if __name__ == "__main__":
    start_time = int(time.time())
    task = task_generators.generate_llm_task()
    print(task)
    print("Time taken to generate task:", int(time.time()) - start_time)
