from hip.utils.misc import get_utc_timestamp
import hip.validator.text_generator as tg
import hip.validator.generators as task_generators

if __name__ == "__main__":
    start_time = get_utc_timestamp()
    task = task_generators.generate_llm_task()
    print(task)
    print("Time taken to generate task:", get_utc_timestamp() - start_time)
