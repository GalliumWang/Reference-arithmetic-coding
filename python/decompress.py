import sys
import tool


def main(args):
	
	if len(args) != 2:
		sys.exit("Usage: python decompress.py InputFile OutputFile")
	inputfile, outputfile = args
	
	
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
	main(sys.argv[1 : ])
