from zmpl import pyplot as zplt

def main():
    fig = zplt.figure(1)
    ax = fig.add_subplot(111)
    zplt.draw()
    print(dir(fig))
    

if __name__ == '__main__':
    main()
