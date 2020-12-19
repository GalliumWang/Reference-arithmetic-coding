import contextlib, sys, os
import tool
import typer


# basic args:input --output --echo --ext

def get_compress_rate(original:str,processed:str)->float:
    originalSize=os.path.getsize(original)
    finalSize=os.path.getsize(processed)
    return  finalSize/originalSize



def main(inputfile: str, outputfile: str = "", echo: bool = False, ext: bool = False):
    if (inputfile.endswith(".compressed")):

        decompressStart(inputfile, outputfile, ext)
    else:
        compressStart(inputfile, outputfile, echo)


def compressStart(inputfile: str, outputfile: str, echo: bool):
    if not outputfile:
        outputfile = "{inputfile}.{extension}".format(inputfile=inputfile, extension="compressed")

    with open(inputfile, "rb") as inp, \
            contextlib.closing(tool.BitOutputStream(open(outputfile, "wb"))) as bitout:
        compress(inp, bitout)

    #TODO option to be added
    cmpRate=get_compress_rate(inputfile,outputfile)
    print("The compress rate: {cmpRate:.2f}%".format(cmpRate=cmpRate))

    if echo:
        with contextlib.closing(tool.BitInputStream(open(outputfile, "rb"))) as inputStream:
            currentChar = inputStream.read()
            while currentChar != -1:
                print(currentChar,end="")
                currentChar = inputStream.read()


def compress(inp, bitout):
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


def decompressStart(inputfile: str, outputfile:str, ext: bool):
    if not outputfile:
        outputfile=inputfile[:-11]
    if ext:
        outputfile="{outputfile}.{extension}".format(outputfile=outputfile,extension="decompressed")
    with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
        bitin = tool.BitInputStream(inp)
        decompress(bitin, out)


def decompress(bitin, out):
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
    typer.run(main)
