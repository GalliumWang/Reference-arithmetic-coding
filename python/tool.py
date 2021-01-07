import os

def get_compress_rate(original: str, processed: str) -> float:
    originalSize = os.path.getsize(original)
    finalSize = os.path.getsize(processed)
    return finalSize / originalSize

class ArithmeticCoderBase:
	def __init__(self, numbits):
		if numbits < 1:
			raise ValueError("State size out of range")
		self.num_state_bits = numbits
		self.full_range = 1 << self.num_state_bits
		self.half_range = self.full_range >> 1
		self.quarter_range = self.half_range >> 1
		self.minimum_range = self.quarter_range + 2
		self.maximum_total = self.minimum_range
		self.state_mask = self.full_range - 1
		self.low = 0
		self.high = self.state_mask
	def update(self, freqs, symbol):
		
		low = self.low
		high = self.high
		if low >= high or (low & self.state_mask) != low or (high & self.state_mask) != high:
			raise AssertionError("Low or high out of range")
		range = high - low + 1
		if not (self.minimum_range <= range <= self.full_range):
			raise AssertionError("Range out of range")
		
		
		total = freqs.get_total()
		symlow = freqs.get_low(symbol)
		symhigh = freqs.get_high(symbol)
		if symlow == symhigh:
			raise ValueError("Symbol has zero frequency")
		if total > self.maximum_total:
			raise ValueError("Cannot code symbol because total is too large")
		
		
		newlow  = low + symlow  * range // total
		newhigh = low + symhigh * range // total - 1
		self.low = newlow
		self.high = newhigh
		
		
		while ((self.low ^ self.high) & self.half_range) == 0:
			self.shift()
			self.low  = ((self.low  << 1) & self.state_mask)
			self.high = ((self.high << 1) & self.state_mask) | 1
		
		
		
		while (self.low & ~self.high & self.quarter_range) != 0:
			self.underflow()
			self.low = (self.low << 1) ^ self.half_range
			self.high = ((self.high ^ self.half_range) << 1) | self.half_range | 1
	
	
	
	def shift(self):
		raise NotImplementedError()
	
	
	
	def underflow(self):
		raise NotImplementedError()




class ArithmeticEncoder(ArithmeticCoderBase):
	
	
	def __init__(self, numbits, bitout):
		super(ArithmeticEncoder, self).__init__(numbits)
		
		self.output = bitout
		
		self.num_underflow = 0

	def write(self, freqs, symbol):
		if not isinstance(freqs, CheckedFrequencyTable):
			freqs = CheckedFrequencyTable(freqs)
		self.update(freqs, symbol)

	def finish(self):
		self.output.write(1)	
	
	
	def shift(self):
		bit = self.low >> (self.num_state_bits - 1)
		self.output.write(bit)
		
		
		for _ in range(self.num_underflow):
			self.output.write(bit ^ 1)
		self.num_underflow = 0
	
	
	def underflow(self):
		self.num_underflow += 1




class ArithmeticDecoder(ArithmeticCoderBase):
	
	
	
	def __init__(self, numbits, bitin):
		super(ArithmeticDecoder, self).__init__(numbits)
		
		self.input = bitin
		
		self.code = 0
		for _ in range(self.num_state_bits):
			self.code = self.code << 1 | self.read_code_bit()
	
	
	
	
	def read(self, freqs):
		if not isinstance(freqs, CheckedFrequencyTable):
			freqs = CheckedFrequencyTable(freqs)
		
		
		total = freqs.get_total()
		if total > self.maximum_total:
			raise ValueError("Cannot decode symbol because total is too large")
		range = self.high - self.low + 1
		offset = self.code - self.low
		value = ((offset + 1) * total - 1) // range
		assert value * range // total <= offset
		assert 0 <= value < total
		
		
		start = 0
		end = freqs.get_symbol_limit()
		while end - start > 1:
			middle = (start + end) >> 1
			if freqs.get_low(middle) > value:
				end = middle
			else:
				start = middle
		assert start + 1 == end
		
		symbol = start
		assert freqs.get_low(symbol) * range // total <= offset < freqs.get_high(symbol) * range // total
		self.update(freqs, symbol)
		if not (self.low <= self.code <= self.high):
			raise AssertionError("Code out of range")
		return symbol
	
	
	def shift(self):
		self.code = ((self.code << 1) & self.state_mask) | self.read_code_bit()
	
	
	def underflow(self):
		self.code = (self.code & self.half_range) | ((self.code << 1) & (self.state_mask >> 1)) | self.read_code_bit()
	
	
	
	
	def read_code_bit(self):
		temp = self.input.read()
		if temp == -1:
			temp = 0
		return temp









class FrequencyTable:
	
	
	def get_symbol_limit(self):
		raise NotImplementedError()
	
	
	def get(self, symbol):
		raise NotImplementedError()
	
	
	
	def set(self, symbol, freq):
		raise NotImplementedError()
	
	
	def increment(self, symbol):
		raise NotImplementedError()
	
	
	
	def get_total(self):
		raise NotImplementedError()
	
	
	
	def get_low(self, symbol):
		raise NotImplementedError()
	
	
	
	def get_high(self, symbol):
		raise NotImplementedError()





class FlatFrequencyTable(FrequencyTable):
	
	
	def __init__(self, numsyms):
		if numsyms < 1:
			raise ValueError("Number of symbols must be positive")
		self.numsymbols = numsyms  
	
	
	def get_symbol_limit(self):
		return self.numsymbols
	
	
	def get(self, symbol):
		self._check_symbol(symbol)
		return 1
	
	
	
	def get_total(self):
		return self.numsymbols
	
	
	
	def get_low(self, symbol):
		self._check_symbol(symbol)
		return symbol
	
	
	
	
	def get_high(self, symbol):
		self._check_symbol(symbol)
		return symbol + 1
	
	
	
	def _check_symbol(self, symbol):
		if 0 <= symbol < self.numsymbols:
			return
		else:
			raise ValueError("Symbol out of range")
	
	
	def __str__(self):
		return "FlatFrequencyTable={}".format(self.numsymbols)
	
	
	def set(self, symbol, freq):
		raise NotImplementedError()
	
	
	def increment(self, symbol):
		raise NotImplementedError()






class SimpleFrequencyTable(FrequencyTable):
	
	
	
	
	
	
	
	def __init__(self, freqs):
		if isinstance(freqs, FrequencyTable):
			numsym = freqs.get_symbol_limit()
			self.frequencies = [freqs.get(i) for i in range(numsym)]
		else:  
			self.frequencies = list(freqs)  
		
		if len(self.frequencies) < 1:
			raise ValueError("At least 1 symbol needed")
		for freq in self.frequencies:
			if freq < 0:
				raise ValueError("Negative frequency")
		
		self.total = sum(self.frequencies)
		
		
		
		self.cumulative = None
	
	
	
	def get_symbol_limit(self):
		return len(self.frequencies)
	
	
	
	def get(self, symbol):
		self._check_symbol(symbol)
		return self.frequencies[symbol]
	
	
	
	
	def set(self, symbol, freq):
		self._check_symbol(symbol)
		if freq < 0:
			raise ValueError("Negative frequency")
		temp = self.total - self.frequencies[symbol]
		assert temp >= 0
		self.total = temp + freq
		self.frequencies[symbol] = freq
		self.cumulative = None
	
	
	
	def increment(self, symbol):
		self._check_symbol(symbol)
		self.total += 1
		self.frequencies[symbol] += 1
		self.cumulative = None
	
	
	
	
	def get_total(self):
		return self.total
	
	
	
	
	def get_low(self, symbol):
		self._check_symbol(symbol)
		if self.cumulative is None:
			self._init_cumulative()
		return self.cumulative[symbol]
	
	
	
	
	def get_high(self, symbol):
		self._check_symbol(symbol)
		if self.cumulative is None:
			self._init_cumulative()
		return self.cumulative[symbol + 1]
	
	
	
	def _init_cumulative(self):
		cumul = [0]
		sum = 0
		for freq in self.frequencies:
			sum += freq
			cumul.append(sum)
		assert sum == self.total
		self.cumulative = cumul
	
	
	
	def _check_symbol(self, symbol):
		if 0 <= symbol < len(self.frequencies):
			return
		else:
			raise ValueError("Symbol out of range")
	
	
	
	
	def __str__(self):
		result = ""
		for (i, freq) in enumerate(self.frequencies):
			result += "{}\t{}\n".format(i, freq)
		return result





class CheckedFrequencyTable(FrequencyTable):
	
	def __init__(self, freqtab):
		
		self.freqtable = freqtab
	
	
	def get_symbol_limit(self):
		result = self.freqtable.get_symbol_limit()
		if result <= 0:
			raise AssertionError("Non-positive symbol limit")
		return result
	
	
	def get(self, symbol):
		result = self.freqtable.get(symbol)
		if not self._is_symbol_in_range(symbol):
			raise AssertionError("ValueError expected")
		if result < 0:
			raise AssertionError("Negative symbol frequency")
		return result
	
	
	def get_total(self):
		result = self.freqtable.get_total()
		if result < 0:
			raise AssertionError("Negative total frequency")
		return result
	
	
	def get_low(self, symbol):
		if self._is_symbol_in_range(symbol):
			low   = self.freqtable.get_low (symbol)
			high  = self.freqtable.get_high(symbol)
			if not (0 <= low <= high <= self.freqtable.get_total()):
				raise AssertionError("Symbol low cumulative frequency out of range")
			return low
		else:
			self.freqtable.get_low(symbol)
			raise AssertionError("ValueError expected")
	
	
	def get_high(self, symbol):
		if self._is_symbol_in_range(symbol):
			low   = self.freqtable.get_low (symbol)
			high  = self.freqtable.get_high(symbol)
			if not (0 <= low <= high <= self.freqtable.get_total()):
				raise AssertionError("Symbol high cumulative frequency out of range")
			return high
		else:
			self.freqtable.get_high(symbol)
			raise AssertionError("ValueError expected")
	
	
	def __str__(self):
		return "CheckedFrequencyTable (" + str(self.freqtable) + ")"
	
	
	def set(self, symbol, freq):
		self.freqtable.set(symbol, freq)
		if not self._is_symbol_in_range(symbol) or freq < 0:
			raise AssertionError("ValueError expected")
	
	
	def increment(self, symbol):
		self.freqtable.increment(symbol)
		if not self._is_symbol_in_range(symbol):
			raise AssertionError("ValueError expected")
	
	
	def _is_symbol_in_range(self, symbol):
		return 0 <= symbol < self.get_symbol_limit()







class BitInputStream:
	
	
	def __init__(self, inp):
		
		self.input = inp
		
		self.currentbyte = 0
		
		self.numbitsremaining = 0
	
	
	
	
	def read(self):
		if self.currentbyte == -1:
			return -1
		if self.numbitsremaining == 0:
			temp = self.input.read(1)
			if len(temp) == 0:
				self.currentbyte = -1
				return -1
			self.currentbyte = temp[0]
			self.numbitsremaining = 8
		assert self.numbitsremaining > 0
		self.numbitsremaining -= 1
		return (self.currentbyte >> self.numbitsremaining) & 1
	
	
	
	
	def read_no_eof(self):
		result = self.read()
		if result != -1:
			return result
		else:
			raise EOFError()
	
	
	
	def close(self):
		self.input.close()
		self.currentbyte = -1
		self.numbitsremaining = 0






class BitOutputStream:
	
	
	def __init__(self, out):
		self.output = out  
		self.currentbyte = 0  
		self.numbitsfilled = 0  
	
	
	
	def write(self, b):
		if b not in (0, 1):
			raise ValueError("Argument must be 0 or 1")
		self.currentbyte = (self.currentbyte << 1) | b
		self.numbitsfilled += 1
		if self.numbitsfilled == 8:
			towrite = bytes((self.currentbyte,))
			self.output.write(towrite)
			self.currentbyte = 0
			self.numbitsfilled = 0
	
	
	
	
	
	def close(self):
		while self.numbitsfilled != 0:
			self.write(0)
		self.output.close()
