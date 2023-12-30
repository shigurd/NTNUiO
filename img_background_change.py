from PIL import Image
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize)

def invert_background_ascii(gif_name):
    img = Image.open(gif_name)
    
    new = []
    for frame_num in range(img.n_frames):
        img.seek(frame_num)
        new_frame = Image.new('RGBA', img.size)
        img_inverse_np = 255 - np.asarray(img)
        print(np.asarray(img))
        print(img_inverse_np)
        img_inverse = Image.fromarray(np.uint8(img_inverse_np))
        #new_frame_inverse_np = (np.asarray(new_frame) - 1) *-1
        new_frame.paste(img_inverse)
        new_frame = new_frame.convert(mode='P', palette=Image.ADAPTIVE)
        #print(np.asarray(new_frame))
        #new_frame_inverse = Image.fromarray(np.uint8(new_frame_inverse_np * 255) , 'P')
        new.append(new_frame)

    new[0].save('new.gif', append_images=new[1:], save_all=True, optimize=False, loop=0)

def create_gif(img_list):
    gif_name = 'new.gif'
    new = []
    
    for i in img_list:
        img = Image.open(i).convert('L')
        img_np = np.array(img)
        #print(img_np)
        img_np[img_np == 255] = 240
        img_modified = Image.fromarray(np.uint8(img_np))
        new.append(img_modified)
    
    new[0].save(gif_name, append_images=new[1:], save_all=True, optimize=True, loop=0)

def show_numpy(img_pth):
    img = Image.open(img_pth).convert('L')
    img_np = np.array(img)
    print(img_np)
    img_np[img_np == 255] = 240
    img_modified = Image.fromarray(np.uint8(img_np))
    img_modified.show()

def background_change_ascii(img_name_list):
    for i, img in enumerate(img_name_list):
        img_name_no_ext, img_ext = img.rsplit('.', 1)
        img_pil = Image.open(img)
        
        new = []
        for frame_num in range(img_pil.n_frames):
            img_pil.seek(frame_num)
            new_frame = Image.new('RGBA', img_pil.size)
            img_np = np.array(img_pil.convert('L'))
            #print(img_np)
            #print(img_np.shape)
            img_np[img_np > 232] = 240
            img_modified = Image.fromarray(np.uint8(img_np))
            #new_frame_inverse_np = (np.asarray(new_frame) - 1) *-1
            new_frame.paste(img_modified)
            new_frame = new_frame.convert(mode='P', palette=Image.ADAPTIVE)
            #print(np.asarray(new_frame))
            #new_frame_inverse = Image.fromarray(np.uint8(new_frame_inverse_np * 255) , 'P')
            new.append(new_frame)

        new[0].save(f'new{i}.{img_ext}', append_images=new[1:], save_all=True, optimize=True, loop=0)

if __name__ =='__main__':
    #create_gif(['ascii-art evolution man0.png', 'ascii-art evolution man1.png', 'ascii-art evolution man2.png', 'ascii-art evolution man3.png', 'ascii-art evolution man4.png', 'ascii-art evolution man5.png', 'ascii-art evolution man6.png'])
    #background_change_ascii(['ascii-art evolution man0.png', 'ascii-art evolution man1.png', 'ascii-art evolution man2.png', 'ascii-art evolution man3.png', 'ascii-art evolution man4.png', 'ascii-art evolution man5.png', 'ascii-art evolution man6.png'])
    background_change_ascii(['ascii-lock0.png'])
