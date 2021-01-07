import contextlib, sys, os
import tool
import typer

app = typer.Typer()


@app.command()
def compress(inputfile: str, echo: bool = False):
    outputfile = "{inputfile}.{extension}".format(inputfile=inputfile, extension="compressed")

    with open(inputfile, "rb") as inp, \
            contextlib.closing(tool.BitOutputStream(open(outputfile, "wb"))) as bitout:
        compressFile(inp, bitout)

    # TODO option to be added
    cmpRate = tool.get_compress_rate(inputfile, outputfile)
    print("压缩率: {cmpRate:.2f}%".format(cmpRate=cmpRate))

    if echo:
        with contextlib.closing(tool.BitInputStream(open(outputfile, "rb"))) as inputStream:
            currentChar = inputStream.read()
            while currentChar != -1:
                print(currentChar, end="")
                currentChar = inputStream.read()


def compressFile(inp, bitout):
    initfreqs = tool.FlatFrequencyTable(257)
    freqs = tool.SimpleFrequencyTable(initfreqs)
    enc = tool.ArithmeticEncoder(32, bitout)
    while True:
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, symbol[0])
        freqs.increment(symbol[0])
    enc.write(freqs, 256)
    enc.finish()


@app.command()
def decompress(inputfile: str):
    if inputfile!= "stdin":
        if inputfile.endswith(".compressed"):
            outputfile = inputfile[:-11]
        else:
            outputfile = inputfile

        with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
            bitin = tool.BitInputStream(inp)
            decompressFile(bitin, out)
    else:
        inputfile="stdin.txt.decompressed"
        outputfile="stdin.txt"
        inputStr = input("输入要解码的二进制串: ")
        with contextlib.closing(tool.BitOutputStream(open(inputfile, "wb"))) as bitout:
            for i in inputStr:
                bitout.write(int(i))
        with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
            bitin = tool.BitInputStream(inp)
            decompressFile(bitin, out)



def decompressFile(bitin, out):
    initfreqs = tool.FlatFrequencyTable(257)
    freqs = tool.SimpleFrequencyTable(initfreqs)
    dec = tool.ArithmeticDecoder(32, bitin)
    while True:

        symbol = dec.read(freqs)
        if symbol == 256:
            break
        out.write(bytes((symbol,)))
        freqs.increment(symbol)


if __name__ == "__main__":
    app()
