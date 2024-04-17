let g:ace_CMakeGenerator=get(g:, 'ace_CMakeGenerator', 'MinGW Makefiles')
let g:ace_BuildPath=get(g:, 'ace_BuildPath', './build')
let g:ace_BuildTypes=get(g:, 'ace_BuildTypes', ['Debug', 'Release'])

function! ace#core#Build()
    wa
    py3 ace_state.build()
endfunction

function! ace#core#Clear()
    py3 ace_state.cmakeHelper.clear()
endfunction

function! ace#core#Target(...)
    let l:activeTarget = ace#python#GetTarget()
    if len(a:000) == 0
        if l:activeTarget == ''
            echo "No target selected"
            return
        endif
        echo l:activeTarget
    else
        let l:target = a:000[0]
        if l:activeTarget != '' && l:activeTarget == l:target
            echo "Already active target"
            return
        endif

        py3 ace_state.setTarget(vim.eval('l:target'))
        call ace#config#Save()
    endif
endfunction

function! ace#core#TargetList(ArgLead, CmdLine, CursorPos)
    " TODO check it inside function and instead just return empty list
    return ace#python#GetTargetsList()
endfunction

function! ace#core#BuildType(...)
    if len(a:000) == 0
        echo ace#python#GetBuildType()
    else
        py3 ace_state.setBuildType(vim.eval('a:000[0]'))
        call ace#config#Save()
    endif
endfunction

function! ace#core#BuildTypeList(ArgLead, CmdLine, CursorPos)
    " TODO check it inside function and instead just return empty list
    return ace#python#GetBuildTypesList()
endfunction

function! ace#core#SwitchBreakpoint()
    py3 ace_state.flipBreakpoint(vim.eval("expand('%:.:p')"), vim.bindeval("line('.')"))
    call ace#config#Save()
endfunction

function! ace#core#ClearBreakpoints()
    py3 ace_state.clearBreakpoints()
endfunction

function! ace#core#PlayButton()
    py3 ace_state.playButton()
    endif
endfunction

function! ace#core#Run()
    call ace#python#Run()
endfunction

function! ace#core#Continue()
    call ace#python#Continue()
endfunction

function! ace#core#Stop()
    py3 ace_state.stop()
endfunction

function! ace#core#StepOver()
    py3 ace_state.stepOver()
endfunction

function! ace#core#StepInto()
    py3 ace_state.stepInto()
endfunction

function! ace#core#StepOut()
    py3 ace_state.stepOut()
endfunction

function! ace#core#Command(cmd)
    py3 print(ace_state.gdbManager.command(vim.eval('a:cmd')))
endfunction

function! s:GetProcessUsedMemory(id)
    if has('win64')
        return system('powershell "Get-Process -Id ' . a:id . ' | Select -ExpandProperty WorkingSet64"')
    elseif has('win32')
        return system('powershell "Get-Process -Id ' . a:id . ' | Select -ExpandProperty WorkingSet"')
    else
        return -1
    endif
endfunction

function! s:OnFileOpened()
    py3 ace_state.onOpenedFileListChanged()
    call ace#config#Save()
endfunction

function! s:OnFileClosed()
    py3 ace_state.onOpenedFileListChanged()
    call ace#config#Save()
endfunction

function! s:OnFileTypeSet()
    " The contents of the command-line window are empty when the filetype is set
    " for the first time. Users should never change its filetype so we only rely
    " on the CmdwinEnter event for that window.
    if !empty( getcmdwintype() )
    return
    endif

   " let &completefunc = {findstart, base -> s:CompleteFunc(findstart, base)}
endfunction

function! ace#core#RequestCompletion(...)
    let l:col = col('.')
    let l:lineNumber = line('.')
    let l:line = l:col > 1 ? getline(lineNumber)[:l:col - 2] : ''
    let l:pos = line2byte( l:lineNumber ) + l:col - 1
    let l:filename = expand('%:.:p')
    let l:proposal = py3eval('ace_state.getIdProposeList(vim.eval("l:filename"), vim.bindeval("l:pos"), vim.eval("l:line"))')
    let l:proposalCount = len(l:proposal)
    if l:proposalCount <= 1
        return ''
    endif
    if l:proposalCount == 2
        call complete(l:col - len(l:proposal[0]), [l:proposal[1]])
        return ''
    endif
    call complete(l:col - len(l:proposal[0]), l:proposal)
    return ''
endfunction

function! s:OnCharTyped(char)
    "call timer_start( 0, function( 'ace#core#RequestCompletion' ) )
endfunction

function! s:OnTextChanged(withPopup)
    "call ace#core#RequestCompletion()
endfunction

function! s:OnCursorMoved()
    "call ace#core#RequestCompletion()
endfunction

function! ace#core#ReplaceId()
    let l:col = col('.')
    let l:lineNumber = line('.')
    let l:line = getline(l:lineNumber)
    let l:pos = line2byte( l:lineNumber ) + l:col - 2
    let l:filename = expand('%:.:p')
    let [l:targetId, l:usages] = py3eval('ace_state.getIdUsageAtPosList(vim.eval("l:filename"), vim.bindeval("l:pos"), vim.eval("l:line"), vim.bindeval("l:col - 1"))')
    if len(l:usages) == 0
        echo 'No suitable id for renaming is under cursor.'
        return
    endif
    let l:replacementId = input('rename "' . l:targetId . '" with: ', l:targetId)
    if len(l:replacementId) == 0 || l:replacementId == l:targetId
        return
    endif

    let l:targetLength = len(l:targetId)
    for [filename, usages] in items(l:usages)
        for usage in usages
            let l:usageLineNumber = byte2line(usage + 1)
            let l:usageLine = getline(l:usageLineNumber)
            let l:usageCol = usage - line2byte(l:usageLineNumber)
            let l:replaceLine = l:usageLine[:l:usageCol] . l:replacementId . l:usageLine[l:usageCol + 1 + l:targetLength:]
            call setline(l:usageLineNumber, l:replaceLine)
            py3 ace_state.updateLine(vim.eval("l:filename"), vim.bindeval("line2byte( l:usageLineNumber ) - 1"), vim.bindeval("line2byte( l:usageLineNumber + 1 ) - 1"), vim.eval("l:replaceLine"))
        endfor
    endfor
endfunction

function! ace#core#DeclareAutocmd()
    augroup aceUpdateWindows
        autocmd!
        autocmd BufEnter * :call s:OnFileOpened()
        autocmd BufDelete * :call s:OnFileClosed()

        " autocmd might be too late and missed some events
        py3 ace_state.onOpenedFileListChanged()

        autocmd FileType * call s:OnFileTypeSet()
        autocmd InsertCharPre * call s:OnCharTyped(v:char)
        autocmd TextChangedI * call s:OnTextChanged(v:false)
        autocmd TextChangedP * call s:OnTextChanged(v:true)
        autocmd CursorMovedI * call s:OnCursorMoved()

        inoremap <A-CR> <C-R>=ace#core#RequestCompletion()<CR>
        nnoremap <S-A-R> :call ace#core#ReplaceId()<CR>
    augroup END
endfunction

let s:coreLoaded=v:false

let s:debugBufName = 'ace_debug'
let s:callStackBufName = 'ace_stack'

function! ace#core#Init()
    if s:coreLoaded
        return
    endif

    call ace#python#Load(g:ace_BuildPath, g:ace_BuildTypes, g:ace_CMakeGenerator, g:ace_ConfigFile)

    call s:LoadCommands()
	call ace#core#DeclareAutocmd()

	" call ace#ui#RegisterBuffer(s:debugBufName, function('ace#render#MemoryGraph'), 0, v:true)
	call ace#ui#RegisterBuffer(s:callStackBufName, function('ace#render#StackInfo'), 1, v:true)

    let s:coreLoaded=v:true
endfunction

function! s:LoadCommands()
    command! -nargs=? -complete=customlist,ace#core#TargetList AceTarget call ace#core#Target(<f-args>)
    command! -nargs=? -complete=customlist,ace#core#BuildTypeList AceBuildType call ace#core#BuildType(<f-args>)
    command! AceBuild call ace#core#Build()
    command! AceClear call ace#core#Clear()

    command! AceRun call ace#core#Run()
    command! AceContinue sil call ace#core#Continue()
    command! AcePlayButton call ace#core#PlayButton()
    command! AceStop call ace#core#Stop()
    command! AceStepOver sil call ace#core#StepOver()
    command! AceStepInto sil call ace#core#StepInto()
    command! AceStepOut sil call ace#core#StepOut()
    command! AceSwitchBreakpoint call ace#core#SwitchBreakpoint()
    command! AceClearBreakpoints sil call ace#core#ClearBreakpoints()
    command! -nargs=1 AceGDBCommand call ace#core#Command(<q-args>)

    nnoremap <F5>  :AcePlayButton<CR>
    nnoremap <C-B> :AceBuild<CR>
    nnoremap <F7>  :AceSwitchBreakpoint<CR>

    nnoremap <C-S-Right> :AceStepOver<CR>
    nnoremap <C-S-Down>  :AceStepInto<CR>
    nnoremap <C-S-Up>    :AceStepOut<CR>
endfunction
