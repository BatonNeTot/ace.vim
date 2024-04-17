
let g:ace_ConfigFile = get(g:, 'ace_ConfigFile', '.ace/config.json')

function! ace#config#IsExist()
    return filereadable(g:ace_ConfigFile)
endfunction

function! ace#config#Save()
    call ace#python#SaveToJson()
endfunction

function! ace#config#Load()
    call ace#python#LoadFronJson()
endfunction