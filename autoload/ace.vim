function! ace#ConfigureProject(...)
    let l:silent = v:false
    if len(a:000) > 0
        let l:silent = a:000[0]
    endif
    
    call ace#core#Init()
    py3 ace_state.configure(vim.bindeval('l:silent'))
endfunction

function! ace#CheckExistingProject()
    if !ace#config#IsExist()
        return
    endif

    call ace#ConfigureProject(v:true)
    call ace#config#Load()
endfunction