-- PCSX-Redux local-only reference capture. No sockets or remote commands.
local ffi = require('ffi')
local frame = 0
local function capture()
    local shot = PCSX.GPU.takeScreenShot()
    local prefix = string.format('frame-%06d', frame)
    local file = assert(io.open(prefix .. '.raw', 'wb'))
    file:write(ffi.string(shot.data.data, shot.data.size))
    file:close()
    local meta = assert(io.open(prefix .. '.json', 'w'))
    meta:write(string.format('{"frame":%d,"width":%d,"height":%d,"bpp":%d}',
        frame, tonumber(shot.width), tonumber(shot.height), tonumber(shot.bpp) or -1))
    meta:close()
    local state = assert(io.open('status.json', 'w'))
    state:write(string.format('{"frame":%d}', frame))
    state:close()
end
oracle_listener = PCSX.Events.createEventListener('GPU::Vsync', function()
    frame = frame + 1
    if frame % 1800 == 0 then
        local ok, err = pcall(capture)
        if not ok then
            local log = assert(io.open('capture-error.txt', 'w'))
            log:write(tostring(err)); log:close()
            PCSX.quit(1)
        end
    end
    if frame >= 18000 then PCSX.quit(0) end
end)
