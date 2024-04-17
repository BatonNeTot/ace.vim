let s:pythonEnabled=v:false

let s:scriptFolderPath = escape( expand( '<sfile>:p:h' ), '\' )

function! ace#python#Load(buildPath, buildTypes, cmakeGenerator, configFile)
	if s:pythonEnabled
		return
	endif
	call s:Init(a:buildPath, a:buildTypes, a:cmakeGenerator, a:configFile)
endfunction

function! s:Init(buildPath, buildTypes, cmakeGenerator, configFile)
    py3 << EOF
import os.path as p
import sys
import configparser
import vim

root_folder = p.normpath( p.join( vim.eval( 's:scriptFolderPath' ), '..', '..' ) )

# Add dependencies to Python path.
sys.path[ 0:0 ] = [ p.join( root_folder, 'python' ) ]

from ace import *
from vimio import *
from gdbmanager import *
from ctags import *

ace_state = ACE(vim.eval('getcwd()'), vim.eval('a:buildPath'), VimIO.adaptStringList(vim.bindeval('a:buildTypes')), vim.eval('a:cmakeGenerator'), vim.eval('a:configFile'))
EOF
    let s:pythonEnabled=v:true
endfunction

function! ace#python#Run()
    py3 ace_state.run()
endfunction

function! ace#python#Continue()
    py3 ace_state.cont()
endfunction

function! ace#python#GetTarget()
	return py3eval('ace_state.getTarget()')
endfunction

function! ace#python#GetTargetsList()
	return py3eval('ace_state.getTargetsList()')
endfunction

function! ace#python#GetBuildType()
	return py3eval('ace_state.getBuildType()')
endfunction

function! ace#python#GetBuildTypesList()
	return py3eval('ace_state.getBuildTypesList()')
endfunction

function! ace#python#SaveToJson()
	py3 ace_state.saveToJson()
endfunction

function! ace#python#LoadFronJson()
	py3 ace_state.loadFromJson()
endfunction

function! ace#python#GetStackList()
	return py3eval('ace_state.getCallStack()')
endfunction