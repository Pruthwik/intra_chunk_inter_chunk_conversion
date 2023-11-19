"""Convert intrachunk data into interchunk in SSF format."""
from argparse import ArgumentParser
from collections import OrderedDict
from re import search


def read_lines_from_file(file_path):
	"""Read lines from a file using its file path."""
	with open(file_path, 'r', encoding='utf-8') as file_read:
		return file_read.readlines()


def write_lines_to_file(lines, file_path):
	"""Write lines to a file."""
	with open(file_path, 'w', encoding='utf-8') as file_write:
		file_write.write('\n'.join(lines))


def create_key_val_pairs_from_morph(morph):
	"""Create key and value pairs from morph text."""
	dict_attrib = {}
	for key_val in morph.split():
		key, val = key_val.split('=')
		dict_attrib[key] = val
	return dict_attrib


def convert_intra_to_inter_chunk_in_sentence(dict_tokens_chunk_wise, name_to_chunk_dict):
	"""Convert intra to inter chunk in a sentence."""
	text_in_sentence = []
	for index_chunk, chunk in enumerate(dict_tokens_chunk_wise):
		if search('([A-Z_]+)\d+', chunk):
			chunk_tag = search('([A-Z_]+)\d+', chunk).group(1)
		else:
			chunk_tag = chunk
		chunk_line = '\t'.join([str(index_chunk + 1), '((', chunk_tag])
		text_in_sentence.append(chunk_line)
		chunk_wise_list = []
		for index_token, token in enumerate(dict_tokens_chunk_wise[chunk]):
			addr, token, pos, morph = token.split('\t')
			addr = str(index_chunk + 1) + '.' + str(index_token + 1)
			morph_text = morph[4: -1]
			morph_attrib = create_key_val_pairs_from_morph(morph_text)
			if 'head' in morph_attrib['chunkType']:
				if 'drel' in morph_attrib:
					drel, parent = morph_attrib['drel'].split(':')
					parent = parent.strip('\'')
					text_in_sentence[-1] = text_in_sentence[-1] + '\t' + '<fs name=\'' + chunk + '\' drel=' + drel + ':' + name_to_chunk_dict[parent] + '\'>'
				else:
					text_in_sentence[-1] = text_in_sentence[-1] + '\t' + '<fs name=\'' + chunk + '\'>'
			af = 'af=' + morph_attrib['af']
			name = 'name=' + morph_attrib['name']
			final_token_morph = ' '.join([af, name])
			final_token_morph = "<fs " + final_token_morph.strip() + ">"
			token_line = '\t'.join([addr, token, pos, final_token_morph])
			chunk_wise_list.append(token_line)
		text_in_sentence += chunk_wise_list
		chunk_wise_list = []
		text_in_sentence.append('\t))')
	return text_in_sentence


def convert_into_inter_chunk_for_file(lines):
	"""Convert into interchunk format for lines in a file."""
	updated_lines = []
	chunk_wise_dict = OrderedDict()
	name_to_chunk_dict = {}
	for line in lines:
		line = line.strip()
		if line:
			if "<Sentence" in line:
				updated_lines.append(line)
			elif "</Sentence>" in line:
				text_in_sentence = convert_intra_to_inter_chunk_in_sentence(chunk_wise_dict, name_to_chunk_dict)
				updated_lines.append('\n'.join(text_in_sentence))
				updated_lines.append(line)
				chunk_wise_dict = OrderedDict()
				name_to_chunk_dict = {}
			else:
				addr, token, pos, morph = line.split('\t')
				token_attrib_dict = create_key_val_pairs_from_morph(morph[4: -1])
				if 'chunkType' in token_attrib_dict:
					chunk_type_with_chunk_name = token_attrib_dict['chunkType']
					chunk_type, chunk_name = chunk_type_with_chunk_name.split(':')
					chunk_name = chunk_name.strip('\'')
					chunk_wise_dict.setdefault(chunk_name, []).append(line)
					if 'chunkId' in token_attrib_dict:
						chunk_id = token_attrib_dict['chunkId'].strip('\'')
						assert chunk_id == chunk_name
						token_name = token_attrib_dict['name']
						token_name = token_name.strip('\'')
						name_to_chunk_dict[token_name] = chunk_id
		else:
			updated_lines.append(line)
	return updated_lines


def main():
	"""Pass arguments and call functions here."""
	parser = ArgumentParser()
	parser.add_argument('--input', dest='inp', help='Enter the input file path')
	parser.add_argument('--output', dest='out', help='Enter the output file path')
	args = parser.parse_args()
	lines = read_lines_from_file(args.inp)
	updated_lines = convert_into_inter_chunk_for_file(lines)
	write_lines_to_file(updated_lines, args.out)


if __name__ == '__main__':
	main()
