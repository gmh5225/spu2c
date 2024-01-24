# SPU To C

from ida_bytes import *
from idaapi import *
from idc import *
import idaapi
import ida_bytes
import idc

#Constants
MASK_ALLSET_128 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
MASK_ALLSET_96  = 0xFFFFFFFFFFFFFFFFFFFFFFFF
MASK_ALLSET_64  = 0xFFFFFFFFFFFFFFFF
MASK_ALLSET_32  = 0xFFFFFFFF
MASK_ALLSET_16  = 0xFFFF

def fsmbi(opcode):
	rt  = opcode & 0x7F
	i44 = (opcode >> 7)  & 0xF
	i43 = (opcode >> 11) & 0xF
	i42 = (opcode >> 15) & 0xF
	i41 = (opcode >> 19) & 0xF
	mask_44 = 0
	mask_43 = 0
	mask_42 = 0
	mask_41 = 0
	i = 0
	while i < 4:
		mask_temp = i44 & (1<<i)
		if mask_temp != 0:
			mask_44 = mask_44 | (0xFF << (i*8))
		i += 1
	i = 0
	while i < 4:
		mask_temp = i43 & (1<<i)
		if mask_temp != 0:
			mask_43 = mask_43 | (0xFF << (i*8))
		i += 1
	i = 0
	while i < 4:
		mask_temp = i42 & (1<<i)
		if mask_temp != 0:
			mask_42 = mask_42 | (0xFF << (i*8))
		i += 1
	i = 0
	while i < 4:
		mask_temp = i41 & (1<<i)
		if mask_temp != 0:
			mask_41 = mask_41 | (0xFF << (i*8))
		i += 1
	cmt = "r{:d}[128b] = 0x{:08X}:{:08X}:{:08X}:{:08X}".format(rt, mask_41,mask_42,mask_43,mask_44)
	return cmt

####################
# Imm shift start: #
####################

def shlqbii(opcode):
	shift  = (opcode >> 14) & 7
	result = MASK_ALLSET_128 << shift
	result &= MASK_ALLSET_128
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	a = (result >> 96) & MASK_ALLSET_32
	b = (result >> 64) & MASK_ALLSET_32
	c = (result >> 32) & MASK_ALLSET_32
	d = result & MASK_ALLSET_32
	cmt    = "r{:d}[128b] = (r{:d} << {:d}) & 0x{:08X}:{:08X}:{:08X}:{:08X}".format(rt,ra,shift,a,b,c,d)

def shlqbyi(opcode):
	shift  = (opcode >> 14) & 0x1F
	shift  *= 8
	result = MASK_ALLSET_128 << shift
	result &= MASK_ALLSET_128
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	a = (result >> 96) & MASK_ALLSET_32
	b = (result >> 64) & MASK_ALLSET_32
	c = (result >> 32) & MASK_ALLSET_32
	d = result & MASK_ALLSET_32
	cmt    = "r{:d}[128b] = (r{:d} << {:d}) & 0x{:08X}:{:08X}:{:08X}:{:08X}".format(rt,ra,shift,a,b,c,d)
	return cmt

def shli(opcode):
	shift  = (opcode >> 14) & 0x3F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	a      = (MASK_ALLSET_32 << shift) & MASK_ALLSET_32
	cmt    = "r{:d}[4x32b] = (r{:d} << {:d}) & 0x{:08X}".format(rt,ra,shift,a)
	return cmt

def shlhi(opcode):
	shift  = (opcode >> 14) & 0x1F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	a      = (MASK_ALLSET_16 << shift) & MASK_ALLSET_16
	cmt    = "r{:d}[8x16b] = (r{:d} << {:d}) & 0x{:04X}".format(rt,ra,shift,a)
	return cmt

#####################
# Imm rotate start: #
#####################

# Right arithm shift 4x32 by bit
def rotmai(opcode):
	shift  = (0 -(opcode >> 14)) & 0x3F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	#fixme: arithm
	cmt    = "r{:d}[4x32b] = (r{:d} >> {:d})".format(rt,ra,shift)
	return cmt

# Right arithm shift 8x16 by bit
def rotmahi(opcode):
	shift  = (0 -(opcode >> 14)) & 0x1F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	#fixme: arithm
	cmt    = "r{:d}[8x16b] = (r{:d} >> {:d})".format(rt,ra,shift)
	return cmt

# Right shift 128 by bit
def rotqmbii(opcode):
	shift  = (0 -(opcode >> 14)) & 0x7
	const  = MASK_ALLSET_128
	result = const >> shift
	result &= MASK_ALLSET_128
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[128b] = (r{:d} >> {:d}) & 0x{:032X}".format(rt,ra,shift,result)
	return cmt

# Right shift 128 by byte
def rotqmbyi(opcode):
	shift  = (0 -(opcode >> 14)) & 0x1F
	shift *= 8
	result = MASK_ALLSET_128 >> shift
	result &= MASK_ALLSET_128
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	# fixme: maybe split in 4 rows? 0s problem.
	cmt    = "r{:d}[128b] = (r{:d} >> {:d}) & 0x{:032X}".format(rt,ra,shift,result)
	return cmt

# Right shift 4x32 by bit
def rotmi(opcode):
	shift  = (0 -(opcode >> 14)) & 0x3F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	a      = MASK_ALLSET_32 >> shift
	cmt    = "r{:d}[4x32b] = (r{:d} >> {:d}) & 0x{:08X}".format(rt,ra,shift,a)
	return cmt

# Right shift 8x16 by bit
def rothmi(opcode):
	shift  = (0 -(opcode >> 14)) & 0x1F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	a      = MASK_ALLSET_16 >> shift
	cmt    = "r{:d}[8x16b] = (r{:d} >> {:d}) & 0x{:04X}".format(rt,ra,shift,a)
	return cmt

# Left rotate 128 by bit
def rotqbii(opcode):
	shift  = (opcode >> 14) & 0x7
	const  = MASK_ALLSET_128
	result1 = const << shift
	result2 = const >> (128-shift)
	result1 &= MASK_ALLSET_128
	result2 &= MASK_ALLSET_128
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	# fixme: maybe split in 4 rows? Ugly
	cmt    = "r{:d}[128b] = (r{:d} << {:d}) & 0x{:032X} | (r{:d} >> {:d}) & 0x{:032X}".format(rt,ra,shift,result1,ra,(128-shift),result2)
	return cmt

# Left rotate 128 by byte
def rotqbyi(opcode):
	shift  = (opcode >> 14) & 0xF
	shift  *= 8
	const  = 0xAAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD
	result = const << shift | const >>( 128-shift)
	result &= MASK_ALLSET_128
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	# fixme: maybe split in 4 rows?
	cmt    = "r{:d}[128b] = r{:d} : {:X}".format(rt,ra,result)
	return cmt

# Left rotate 4x32 by bit
def roti(opcode):
	#fixme: shift is signed?
	shift  = (opcode >> 14) & 0x1F
	result1 = MASK_ALLSET_32 << shift
	result2 = MASK_ALLSET_32 >> (32-shift)
	result1 &= MASK_ALLSET_32
	result2 &= MASK_ALLSET_32
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[4x32b] = (r{:d} << {:d}) & 0x{:08X} | (r{:d} >> {:d}) & 0x{:08X}".format(rt,ra,shift,result1,ra,(32-shift),result2)
	return cmt

# Left rotate 8x16 by bit
def rothi(opcode):
	shift  = (opcode >> 14) & 0xF
	result1 = MASK_ALLSET_16 << shift
	result2 = MASK_ALLSET_16 >> (16-shift)
	result1 &= MASK_ALLSET_16
	result2 &= MASK_ALLSET_16
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	# we can have special case here:
	if shift == 8:
		cmt    = "r{:d}[8x16b] = byteswap16(r{:d})".format(rt,ra)
		return cmt
	cmt    = "r{:d}[8x16b] = (r{:d} << {:d}) & 0x{:04X} | (r{:d} >> {:d}) & 0x{:04X}".format(rt,ra,shift,result1,ra,(16-shift),result2)
	return cmt

#########################
# Non imm rotate start: #
#########################

# Right arithm shift 4x32 by bit from rb
def rotma(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	#fixme: arithm
	cmt    = "r{:d}[4x32b] = (r{:d} >> -(r{:d}) & 0x3F))".format(rt,ra,rb)
	return cmt

# Right arithm shift 8x16 by bit from rb
def rotmah(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	#fixme: arithm
	cmt    = "r{:d}[8x16b] = r{:d} >> -(r{:d}) & 0x1F".format(rt,ra,rb)
	return cmt

# Right shift 128 by bit from rb
def rotqmbi(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[128b] = r{:d} >> -(r{:d}) & 7".format(rt,ra,rb)
	return cmt

# Right shift 128 by byte from rb
# fixme rotqmby
def rotqmbybi(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[128b] = (r{:d} >> (( -(r{:d}) & 0x1F) * 8))".format(rt,ra,rb)
	return cmt

# Right shift 128 by byte from rb
# fixme rotqmbybi
def rotqmby(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[128b] = r{:d} >> (( -(r{:d}) & 0x1F) * 8)".format(rt,ra,rb)
	return cmt

# Right logical shift 4x32 by bit from rb
def rotm(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[4x32b] = r{:d} >> -(r{:d}) & 0x3F".format(rt,ra,rb)
	return cmt

# Right logical shift 8x16 by bit from rb
def rothm(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[8x16b] = r{:d} >> -(r{:d}) & 0x1F".format(rt,ra,rb)
	return cmt

# Left rotate 128 by bit from rb
def rotqbi(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[128b] = r{:d} << (r{:d} & 7) | r{:d} >> (128 - (r{:d} & 7))".format(rt,ra,rb,ra,rb)
	return cmt

#rotqbybi

# Left rotate 128 by byte from rb
def rotqby(opcode):
	rb  = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[128b] = r{:d} << ((r{:d} & 0xF) * 8) | r{:d} >> (128 - ((r{:d} & 0xF) * 8))".format(rt,ra,rb,ra,rb)
	return cmt

# Left rotate 4x32 by bit from rb
def rot(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[4x32b] = r{:d} << (r{:d} & 0x1F) | r{:d} >> (32 - (r{:d} & 0x1F))".format(rt,ra,rb,ra,rb)
	return cmt

# Left rotate 8x16 by bit from rb
def roth(opcode):
	rb     = (opcode >> 14) & 0x7F
	ra     = (opcode >> 7) & 0x7F
	rt     = opcode & 0x7F
	cmt    = "r{:d}[8x16b] = r{:d} << (r{:d} & 0xF) | r{:d} >> (16 - (r{:d} & 0xF))".format(rt,ra,rb,ra,rb)
	return cmt


# Todo:
# imm:
# mpyi, mpyui, sfi, sfhi, ai (signed i10), ahi (signed i10), iohl, ilhu
# non imm:
# shifts, compares, orx, xswd. xshw, xsbh, rotqbybi
# else: simplify x by 0

def SPUAsm2C(addr):

	opcode = get_wide_dword(addr)
	opcode_name = print_insn_mnem(addr)
	if opcode_name == "fsmbi":
		return fsmbi(opcode)
	elif opcode_name == "shlqbyi":
		return shlqbyi(opcode)
	elif opcode_name == "shlqbii":
		return shlqbii(opcode)
	elif opcode_name == "shli":
		return shli(opcode)
	elif opcode_name == "shlhi":
		return shlhi(opcode)
	elif opcode_name == "rotmai":
		return rotmai(opcode)
	elif opcode_name == "rotmahi":
		return rotmahi(opcode)
	elif opcode_name == "rotqmbii":
		return rotqmbii(opcode)
	elif opcode_name == "rotqmbyi":
		return rotqmbyi(opcode)
	elif opcode_name == "rotmi":
		return rotmi(opcode)
	elif opcode_name == "rothmi":
		return rothmi(opcode)
	elif opcode_name == "rotqbii":
		return rotqbii(opcode)
	elif opcode_name == "rotqbyi":
		return rotqbyi(opcode)
	elif opcode_name == "roti":
		return roti(opcode)
	elif opcode_name == "rothi":
		return rothi(opcode)
	elif opcode_name == "rotma":
		return rotma(opcode)
	elif opcode_name == "rotmah":
		return rotmah(opcode)
	elif opcode_name == "rotqmbi":
		return rotqmbi(opcode)
	elif opcode_name == "rotqmbybi":
		return rotqmbybi(opcode)
	elif opcode_name == "rotqmby":
		return rotqmby(opcode)
	elif opcode_name == "rotm":
		return rotm(opcode)
	elif opcode_name == "rothm":
		return rothm(opcode)
	elif opcode_name == "rotqbi":
		return rotqbi(opcode)
	elif opcode_name == "rotqby":
		return rotqby(opcode)
	elif opcode_name == "rot":
		return rot(opcode)
	elif opcode_name == "roth":
		return roth(opcode)

	return 0

def run_task(start_addr, end_addr, always_insert_comment):

	# convert all instructions within the bounds
	addr = start_addr
	while(addr < end_addr):
		print_str = SPUAsm2C(addr)
		if(print_str != 0 and print_str != 1):
			set_cmt(addr, print_str, False)
		elif (print_str == 0 and always_insert_comment == True):
			msg("0x{:X}: Error converting SPU to C code\n".format(addr))
		addr += 4


def PluginMain():

	# select current line or selected lines
	always_insert_comment = False
	start_addr = read_selection_start()
	end_addr = read_selection_end()
	if(start_addr == BADADDR):
		start_addr = get_screen_ea();
		end_addr = start_addr + 4;
		always_insert_comment = True

	run_task(start_addr, end_addr, always_insert_comment)


def PluginMainF():

	# convert current function
	p_func = get_func(get_screen_ea());
	if(p_func == None):
		msg("Not in a function, so can't do SPU to C conversion for the current function!\n");
		return;
	start_addr = p_func.start_ea;
	end_addr = p_func.end_ea;
	always_insert_comment = False;

	run_task(start_addr, end_addr, always_insert_comment)


#/***************************************************************************************************
#*
#*	Strings required for IDA Pro's PLUGIN descriptor block
#*
#***************************************************************************************************/
#
G_PLUGIN_COMMENT = "SPU To C Conversion Assist"
G_PLUGIN_HELP = "This plugin assists in converting SPU instructions into their relevant C code.\nIt is especially useful for the tricky bit manipulation and shift instructions.\n"
G_PLUGIN_NAME = "SPU To C: Selected Lines"

#/***************************************************************************************************
#*
#*	This 'PLUGIN' data block is how IDA Pro interfaces with this plugin.
#*
#***************************************************************************************************/

class ActionHandler(idaapi.action_handler_t):

    def __init__(self, callback):

        idaapi.action_handler_t.__init__(self)
        self.callback = callback

    def activate(self, ctx):

        self.callback()
        return 1

    def update(self, ctx):

        return idaapi.AST_ENABLE_ALWAYS

def register_actions():

    actions = [
        {
            'id': 'start:plg',
            'name': G_PLUGIN_NAME,
            'hotkey': 'F10',
            'comment': G_PLUGIN_COMMENT,
            'callback': PluginMain,
            'menu_location': 'Start Plg'
        },
        {
            'id': 'start:plg1',
            'name': 'spu2c unimplemented',
            'hotkey': 'Alt-Shift-F10',
            'comment': G_PLUGIN_COMMENT,
            'callback': PluginMainF,
            'menu_location': 'Start Plg1'
        }
    ]

    for action in actions:

        if not idaapi.register_action(idaapi.action_desc_t(
            action['id'], # Must be the unique item
            action['name'], # The name the user sees
            ActionHandler(action['callback']), # The function to call
            action['hotkey'], # A shortcut, if any (optional)
            action['comment'] # A comment, if any (optional)
        )):

            print('Failed to register ' + action['id'])

        if not idaapi.attach_action_to_menu(
            action['menu_location'], # The menu location
            action['id'], # The unique function ID
            0):

            print('Failed to attach to menu '+ action['id'])

class spu_helper_t(idaapi.plugin_t):
	flags = idaapi.PLUGIN_HIDE
	comment = G_PLUGIN_COMMENT
	help = G_PLUGIN_HELP
	wanted_name = G_PLUGIN_NAME
	wanted_hotkey = "F10"

	def init(self):
		if (idaapi.ph.id == idaapi.PLFM_SPU):
			register_actions()
			idaapi.msg("spu2c: loaded\n")
			return idaapi.PLUGIN_KEEP

		return idaapi.PLUGIN_SKIP

	def run(self, arg):
		idaapi.msg("spu2c: run\n")

	def term(self):
		pass

def PLUGIN_ENTRY():
	return spu_helper_t()