let s:buffers = {}

function! ace#ui#RegisterBuffer(name, renderer, order, temp)
    let l:buffer = {'name':a:name, 'renderer' : a:renderer, 'order' : a:order, 'temp' : a:temp, 'opened' : v:false}
    let s:buffers[a:name] = l:buffer
    return l:buffer
endfunction

function! ace#ui#OpenBuffer(name)
    let l:buffer = s:buffers[a:name]

    if l:buffer.opened
        call s:GotoOpenedBuffer(a:name)
    else
        if l:buffer.temp
            call s:OpenTempBuffer(l:buffer)
        else
            " TODO isn't supported
        endif
        let l:buffer.opened = v:true
    endif

    call s:Render(l:buffer.renderer)
endfunction

function! s:OpenTempBuffer(buffer)
    let l:splitLocation = 'botright '
    let l:splitDirection = 'vertical'
    let l:splitSize = 31

    silent! execute l:splitLocation . l:splitDirection . ' ' . l:splitSize . ' new'
    silent! execute 'edit ' . a:buffer.name
    silent! execute l:splitDirection . ' resize '. l:splitSize

    setlocal winfixwidth
    
    " Options for a non-file/control buffer.
    setlocal bufhidden=delete
    setlocal buftype=nofile
    setlocal noswapfile

    " Options for controlling buffer/window appearance.
    setlocal foldcolumn=0
    setlocal foldmethod=manual
    setlocal nobuflisted
    setlocal nofoldenable
    setlocal nolist
    setlocal nospell
    setlocal nowrap

    setlocal nonumber
    if v:version >= 703
        setlocal norelativenumber
    endif

    iabc <buffer>

    setlocal filetype=ace_debug
endfunction

let s:currentWindowId = 0

function! s:StoreWindow()
    let s:currentWindowId = win_getid()
endfunction

function! s:RestoreWindow()
    call win_gotoid(s:currentWindowId)
endfunction

function! s:StoreWindowState()
    " remember the top line of the buffer and the current line so we can
    " restore the view exactly how it was
    let s:windowCurLine = line('.')
    let s:windowCurCol = col('.')
    let s:windowTopLine = line('w0')

endfunction

function! s:RestoreWindowState()
    " restore the view
    let old_scrolloff=&scrolloff
    let &scrolloff=0
    call cursor(s:windowTopLine, 1)
    normal! zt
    call cursor(s:windowCurLine, s:windowCurCol)
    let &scrolloff = old_scrolloff
endfunction

function! s:RenderWithRestore(func)
    setlocal noreadonly modifiable

    call s:StoreWindowState()

    call s:RenderImpl(a:func)

    call s:RestoreWindowState()

    setlocal readonly nomodifiable
endfunction

function! s:Render(func)
    setlocal noreadonly modifiable

    call s:RenderImpl(a:func)

    setlocal readonly nomodifiable
endfunction

function! s:GetStackTrace()
    try
        throw 0
    catch
        return v:throwpoint
    endtry
endfunction

function! s:PrintStackTrace()
    echo s:GetStackTrace()
endfunction

function! s:RenderImpl(func)
    " delete all lines in the buffer (being careful not to clobber a register)
    silent 1,$delete _

    " draw
    let l:currentWindowSpecialId = 0
    let l:width = winwidth(l:currentWindowSpecialId)
    let l:height = winheight(l:currentWindowSpecialId)

    let print = a:func(l:width, l:height)
    silent! put =print

    " delete the blank line at the top of the buffer
    silent 1,1delete _
endfunction

function! s:GotoOpenedBuffer(bufname)
    call win_gotoid(bufwinid(a:bufname)) 
endfunction

function! ace#ui#UpdateBuffers()
    call s:StoreWindow()

    for l:buffer in values(s:buffers)
        if l:buffer.opened
            call s:GotoOpenedBuffer(l:buffer.name)
            call s:Render(l:buffer.renderer)
        endif
    endfor

    call s:RestoreWindow()
endfunction

function! ace#ui#OpenDebugWindows()
    call s:StoreWindow()
    
    for l:buffer in values(s:buffers)
        if !l:buffer.opened
            call ace#ui#OpenBuffer(l:buffer.name)
        endif
    endfor

    call s:RestoreWindow()
endfunction

function! s:OnFileOpened()

endfunction

function! s:OnFileClosed()

endfunction

function! s:DeclareAuto()
    augroup aceUpdateDebugBuffers
        autocmd!
        autocmd VimResized * call ace#ui#UpdateBuffers()
        autocmd WinScrolled * call ace#ui#UpdateBuffers()

        autocmd BufCreate * :call s:OnFileOpened()
        autocmd BufDelete * :call s:OnFileClosed()
    augroup END
endfunction

call s:DeclareAuto()