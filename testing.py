from tenacity import retry, stop_after_attempt, wait_exponential


counter = 0


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=4, max=15))
def test_function():
    raise Exception("test")


test_function()
