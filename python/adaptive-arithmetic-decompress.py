import sys
import arithmeticcoding


def main(args):
	
	if len(args) != 2:
		sys.exit("Usage: python adaptive-arithmetic-decompress.py InputFile OutputFile")
	inputfile, outputfile = args
	
	
	with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
		bitin = arithmeticcoding.BitInputStream(inp)
		decompress(bitin, out)


def decompress(bitin, out):
	initfreqs = arithmeticcoding.FlatFrequencyTable(257)
	freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
	dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
	while True:
		
		symbol = dec.read(freqs)
		if symbol == 256:  
			break
		out.write(bytes((symbol,)))
		freqs.increment(symbol)


if __name__ == "__main__":
	main(sys.argv[1 : ])
