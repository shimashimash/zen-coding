#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Filter that produces HTML tree
@author Sergey Chikuyonok (serge.che@gmail.com)
@link http://chikuyonok.ru
'''
from zencoding import zen_core as zen_coding

child_token = '${child}'

def make_attributes_string(tag, profile):
	"""
	Creates HTML attributes string from tag according to profile settings
	@type tag: ZenNode
	@type profile: dict
	"""
	# make attribute string
	attrs = ''
	attr_quote = profile['attr_quotes'] == 'single' and "'" or '"'
	cursor = profile['place_cursor'] and zen_coding.get_caret_placeholder() or ''
	
	# process other attributes
	for a in tag.attributes:
		attr_name = profile['attr_case'] == 'upper' and a['name'].upper() or a['name'].lower()
		attrs += ' ' + attr_name + '=' + attr_quote + (a['value'] or cursor) + attr_quote
		
	return attrs

def process_snippet(item, profile, level):
	"""
	Processes element with <code>snippet</code> type
	@type item: ZenNode
	@type profile: dict
	@type level: int
	"""
	data = item.source.value;
		
	if not data:
		# snippet wasn't found, process it as tag
		return process_tag(item, profile, level)
		
	start, end = data.split(child_token)
	if not end: end = ''
	padding = item.parent and item.parent.padding or ''
		
	
	item.start = item.start % zen_coding.pad_string(start, padding)
	item.end = item.end % zen_coding.pad_string(end, padding)
	
	return item


def has_block_sibling(item):
	"""
	Test if passed node has block-level sibling element
	@type item: ZenNode
	@return: bool
	"""
	return item.parent and item.parent.has_block_children()

def process_tag(item, profile, level):
	"""
	Processes element with <code>tag</code> type
	@type item: ZenNode
	@type profile: dict
	@type level: int
	"""
	if not item.name:
		# looks like it's root element
		return item
	
	attrs = make_attributes_string(item, profile) 
	cursor = profile['place_cursor'] and zen_coding.get_caret_placeholder() or ''
	self_closing = ''
	is_unary = item.is_unary() and not item.children
	start= ''
	end = ''
	
	if profile['self_closing_tag'] == 'xhtml':
		self_closing = ' /'
	elif profile['self_closing_tag'] is True:
		self_closing = '/'
		
	# define opening and closing tags
	tag_name = profile['tag_case'] == 'upper' and item.name.upper() or item.name.lower()
	if is_unary:
		start = '<' + tag_name + attrs + self_closing + '>'
		item.end = ''
	else:
		start = '<' + tag_name + attrs + '>'
		end = '</' + tag_name + '>'
	
	item.start = item.start % start
	item.end = item.end % end
	
	if not item.children and not is_unary:
		item.start += cursor
	
	return item

def process(tree, profile, level=0):
	"""
	Processes simplified tree, making it suitable for output as HTML structure
	@type tree: ZenNode
	@type profile: dict
	@type level: int
	"""
	if level == 0:
		tree = zen_coding.run_filters(tree, profile, '_format')
	
	if level == 0:
		# preformat tree
		tree = zen_coding.run_filters(tree, profile, '_format')
		
	for i, item in enumerate(tree.children):
		if item.type == 'tag':
			process_tag(item, profile, level)
		else:
			process_snippet(item, profile, level)
	
		# replace counters
		item.start = zen_coding.replace_counter(item.start, i + 1)
		item.end = zen_coding.replace_counter(item.end, i + 1)
		process(item, profile, level + 1)
		
	return tree

zen_coding.register_filter('html', process)