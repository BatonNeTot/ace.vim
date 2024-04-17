" Title:        All-in-One C Editor
" Description:  A plugin to cover all needs for C development.
" Last Change:  30 Jule 2024
" Maintainer:   Georgii Fedorov <https://github.com/BatonNeTot>

" Prevents the plugin from being loaded multiple times. If the loaded
" variable exists, do nothing more. Otherwise, assign the loaded
" variable and continue running this instance of the plugin.
if exists("g:ace_loaded")
    finish
endif
let g:ace_loaded = v:true

" Exposes the plugin's functions for use as commands in Vim.
command! AceConfigure call ace#ConfigureProject()

if v:vim_did_enter
    sil call ace#CheckExistingProject()
else
    augroup aceStart
        autocmd!
        autocmd VimEnter * sil call ace#CheckExistingProject()
    augroup END
endif

