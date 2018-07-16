import asyncio
import time


def long_task():
    time.sleep(100)



async def fa():
    # await long_task()
    print('start')
    # asyncio.sleep(10)
    time.sleep(5)
    print('done')


async def ff():
    print('hello')
    await asyncio.sleep(5)
    # await fa()


async def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    await asyncio.sleep(5)
    return x + y


async def print_sum(x, y):
    result = await compute(x, y)
    print("%s + %s = %s" % (x, y, result))


# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(ff())
#     loop.run_until_complete(print_sum(1, 2))
#     loop.close()


def run(f):
    try:
        a = f()
        a.send(None)
    except:
        return "not ok"


run(fa)
