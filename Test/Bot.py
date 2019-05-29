import time


def instance(arg, pipe):
    # try:
    while True:
        arg = arg
        time.sleep(5)
        # if pipe.poll():
        #     inputtext = pipe.recv(10)
        #     if inputtext == "exit":
        #         exit(1)
        # time.sleep(2)
    # except Exception as errormsg:
    #     with open(arg + "_error.txt", "w+") as f:
    #         f.write(errormsg)


if __name__ == '__main__':
    print("Main function triggered.")
