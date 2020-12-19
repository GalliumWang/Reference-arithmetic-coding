
import contextlib, sys
import arithmeticcoding


def main(args):
	
	if len(args) != 2:
		sys.exit("Usage: python adaptive-arithmetic-compress.py InputFile OutputFile")
	inputfile, outputfile = args
	
	
	with open(inputfile, "rb") as inp, \
			contextlib.closing(arithmeticcoding.BitOutputStream(open(outputfile, "wb"))) as bitout:
		compress(inp, bitout)


def compress(inp, bitout):
	initfreqs = arithmeticcoding.FlatFrequencyTable(257)
	freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
	enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
	while True:
		
		symbol = inp.read(1)
		if len(symbol) == 0:
			break
		enc.write(freqs, symbol[0])
		freqs.increment(symbol[0])
	enc.write(freqs, 256)  
	enc.finish()  



if __name__ == "__main__":
	main(sys.argv[1 : ])
