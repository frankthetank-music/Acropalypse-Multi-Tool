import zlib
import sys
import io
import struct
import requests
from urllib.parse import urlparse

import tempfile
import os

tempdir = tempfile.gettempdir()

class Acropalypse():
	def parse_png_chunk(self, stream):
		size = int.from_bytes(stream.read(4), "big")
		ctype = stream.read(4)
		body = stream.read(size)
		csum = int.from_bytes(stream.read(4), "big")
		assert(zlib.crc32(ctype + body) == csum)
		return ctype, body

	def pack_png_chunk(self, stream, name, body):
		stream.write(len(body).to_bytes(4, "big"))
		stream.write(name)
		stream.write(body)
		crc = zlib.crc32(body, zlib.crc32(name))
		stream.write(crc.to_bytes(4, "big"))
	def reconstruct_image(self, cropped_image_file, img_width, img_heigth, mode):
		PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

		orig_width = img_width
		orig_height = img_heigth

		f_in = open(cropped_image_file, "rb")
		magic = f_in.read(len(PNG_MAGIC))
		assert(magic == PNG_MAGIC)

		# find end of cropped PNG
		while True:
			ctype, body = self.parse_png_chunk(f_in)
			if ctype == b"IEND":
				break

		# grab the trailing data
		trailer = f_in.read()
		
		print(f"Found {len(trailer)} trailing bytes!")

		# find the start of the nex idat chunk
		try:
			next_idat = trailer.index(b"IDAT", 12)
		except ValueError:
			raise Exception("No trailing IDATs found!")

		# skip first 12 bytes in case they were part of a chunk boundary
		idat = trailer[12:next_idat-8] # last 8 bytes are crc32, next chunk len

		stream = io.BytesIO(trailer[next_idat-4:])

		while True:
			ctype, body = self.parse_png_chunk(stream)
			if ctype == b"IDAT":
				idat += body
			elif ctype == b"IEND":
				break
			else:
				raise Exception("Unexpected chunk type: " + repr(ctype))

		idat = idat[:-4] # slice off the adler32

		print(f"Extracted {len(idat)} bytes of idat!")

		print("building bitstream...")
		bitstream = []
		for byte in idat:
			for bit in range(8):
				bitstream.append((byte >> bit) & 1)

		# add some padding so we don't lose any bits
		for _ in range(7):
			bitstream.append(0)

		print("reconstructing bit-shifted bytestreams...")
		byte_offsets = []
		for i in range(8):
			shifted_bytestream = []
			for j in range(i, len(bitstream)-7, 8):
				val = 0
				for k in range(8):
					val |= bitstream[j+k] << k
				shifted_bytestream.append(val)
			byte_offsets.append(bytes(shifted_bytestream))

		# bit wrangling sanity checks
		assert(byte_offsets[0] == idat)
		assert(byte_offsets[1] != idat)

		print("Scanning for viable parses...")

		# prefix the stream with 32k of "X" so backrefs can work
		prefix_lenght = 0x8000
		prefix = b"\x00" + (prefix_lenght).to_bytes(2, "little") + (prefix_lenght ^ 0xffff).to_bytes(2, "little") + b"\x00" * prefix_lenght

		for i in range(len(idat)):
			truncated = byte_offsets[i%8][i//8:]

			# only bother looking if it's (maybe) the start of a non-final adaptive huffman coded block
			if truncated[0]&7 != 0b100:
				continue

			d = zlib.decompressobj(wbits=-15)
			try:
				decompressed = d.decompress(prefix+truncated) + d.flush(zlib.Z_FINISH)
				decompressed = decompressed[prefix_lenght:] # remove leading padding
				if d.eof and d.unused_data in [b"", b"\x00"]: # there might be a null byte if we added too many padding bits
					print(f"Found viable parse at bit offset {i}!")
					# XXX: maybe there could be false positives and we should keep looking?
					break
				else:
					print(f"Parsed until the end of a zlib stream, but there was still {len(d.unused_data)} byte of remaining data. Skipping.")
			except zlib.error as e: # this will happen almost every time
				#print(e)
				pass
		else:
			raise Exception("Failed to find viable parse!")

		print("Generating output PNG...")

		out = open(os.path.join(tempdir, 'restored.png'), "wb")

		out.write(PNG_MAGIC)

		ihdr = b""
		ihdr += orig_width.to_bytes(4, "big")
		ihdr += orig_height.to_bytes(4, "big")
		ihdr += (8).to_bytes(1, "big") # bitdepth
		if mode == "Windows 11 Snipping Tool":
			ihdr += (6).to_bytes(1, "big") # true colour with alpha
		else:
			ihdr += (2).to_bytes(1, "big") # true colour
		ihdr += (0).to_bytes(1, "big") # compression method
		ihdr += (0).to_bytes(1, "big") # filter method
		ihdr += (0).to_bytes(1, "big") # interlace method

		self.pack_png_chunk(out, b"IHDR", ihdr)

		# fill missing data with solid magenta
		if mode == "Windows 11 Snipping Tool":
			reconstructed_idat = bytearray((b"\x00" + b"\xff\x00\xff\xff" * orig_width) * orig_height)
		else:
			reconstructed_idat = bytearray((b"\x00" + b"\xff\x00\xff" * orig_width) * orig_height)

		# paste in the data we decompressed
		reconstructed_idat[-len(decompressed):] = decompressed

		self.pack_png_chunk(out, b"IDAT", zlib.compress(reconstructed_idat))
		self.pack_png_chunk(out, b"IEND", b"")

		print("Done!")

	def fetch_data(self, input_source):
		if self.is_url(input_source):
			return self.fetch_remote_data(input_source)
		else:
			return self.fetch_local_data(input_source)

	def is_url(self, input_source):
		try:
			result = urlparse(input_source)
			return result.scheme in ('http', 'https')
		except ValueError:
			return False

	def fetch_local_data(self, filepath):
		try:
			with open(filepath, 'rb') as file:
				data = file.read()
				return data
		except FileNotFoundError:
			print(f"File not found: {filepath}")
			return None

	def fetch_remote_data(self, url):
		response = requests.get(url)
		if response.status_code != 200:
			print(f"Failed to fetch the PNG file from the URL: {url}")
			return None
		return response.content

	def detect_png(self, input_source):
		data = self.fetch_data(input_source)
		if not data:
			return

		png_signature = b'\x89PNG\r\n\x1a\n'
		iend_chunk = b'IEND'

		if not data.startswith(png_signature):
			return f"The file at {input_source} is not a valid PNG file."

		iend_index = data.find(iend_chunk)

		if iend_index == -1:
			return f"The file at {input_source} is not a valid PNG file."

		iend_length = 4
		crc_length = 4
		iend_full_chunk_length = iend_length + crc_length

		if len(data) > iend_index + iend_full_chunk_length:
			return True
		else:
			return False
