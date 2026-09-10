"""Read current player and door coordinates using the matched reference layout."""
import json
import socket
import struct

def command(cmd, **fields):
    with socket.create_connection(('127.0.0.1',18765),timeout=5) as conn:
        conn.sendall((json.dumps(dict(cmd=cmd,**fields))+'\n').encode())
        data=bytearray()
        while chunk:=conn.recv(65536): data.extend(chunk)
    return json.loads(data)

def memory(address, size):
    if not 0x80000000 <= address < 0x80200000 or address+size > 0x80200000:
        raise ValueError('Read outside main RAM')
    return bytes.fromhex(command('read_ram',addr=f'{address:08X}',len=size)['hex'])

def state():
    actor=struct.unpack('<I',memory(0x800F19FC,4))[0]
    transform=struct.unpack('<I',memory(actor+0x44,4))[0]
    data=memory(transform,104)
    room=memory(0x800F1AB0,12)
    header=memory(0x800F1BF8,116)
    size=struct.unpack_from('<I',header,16)[0]
    pointer=struct.unpack_from('<I',header,112)[0]
    if size > 12*256 or size%12:
        raise ValueError('Invalid door section size')
    doors=[]
    if size:
        for znd,mpd,grid,pos1,pos2,extra in struct.iter_unpack('<BBHHH4s',memory(pointer,size)):
            doors.append(dict(destination=[znd,mpd],tile=[grid&31,(grid>>5)&31],layer=(grid>>10)&1,
                              packed_position=[pos1,pos2]))
    position=struct.unpack_from('<3h',data,0x1c)
    return dict(room=list(room[:2]),tile=[data[0x5c],data[0x5e]],position=list(position),
                facing=struct.unpack_from('<h',data,0x26)[0],doors=doors)

if __name__=='__main__':
    print(json.dumps(state(),indent=2))
