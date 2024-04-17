
let s:memValues = [3,8,5]
let s:memValueMax = 8
let s:memXMax = 10

function! ace#render#MemoryGraph(width, height)
    let l:memValuesCount = len(s:memValues)
    if l:memValuesCount <= 0
        return ''
    elseif l:memValuesCount == 1
        return s:RenderValueAsColumn(get(s:memValues, 0), a:width, s:memXMax)
    endif

    let lines = [] 

    let startMemIndex = 0
    let endMemIndex = 1

    for i in range(0, a:height)
        let progress = floor(i * (l:memValuesCount - 1)) / floor(a:height)
        let index = float2nr(floor(progress))

        if (index >= endMemIndex)
            let startMemIndex = endMemIndex
            let endMemIndex = index + 1
        endif

        let startMemValue = get(s:memValues, startMemIndex)
        let endMemValue = get(s:memValues, endMemIndex)

        let coeff = (progress - floor(startMemIndex)) / floor(endMemIndex - startMemIndex)

        let memValue = startMemValue + coeff * (endMemValue - startMemValue)
        call add(lines, s:RenderValueAsColumn(memValue, a:width, s:memXMax))
    endfor

    "let print = s:GetProcessUsedMemory(5760)
    return lines
endfunction

function! s:RenderValueAsColumn(value, width, maxXValue)
    let size = float2nr(round(floor(a:value * a:width) / floor(a:maxXValue)))
    return repeat('*', size)
endfunction

function! ace#render#StackInfo(width, height)
    return ace#python#GetStackList()
endfunction