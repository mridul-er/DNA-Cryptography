import secrets
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr


#Codon Sequences
codon_a=['ATT', 'ACT', 'AAT', 'AGT', 'ATC', 'ACC','AAC','AGC','ATA','ACA','AAA','AGA','ATG','ACG','AAG','AGG']
codon_t=['TTT', 'TCT','TAT', 'TGT','TTC', 'TCC', 'TAC', 'TGC', 'TTA', 'TCA', 'TAA', 'TGA', 'TTG','TCG','TAG','TGG']
codon_g=['GTT','GCT','GAT','GGT','GTC','GCC','GAC','GGC','GTA','GCA','GAA','GGA','GTG','GCG','GAG','GGG']
codon_c=['CTT','CCT','CAT','CGT','CTC','CCC','CAC','CGC','CTA','CCA','CAA','CGA','CTG','CCG','CAG','CGG']

codon_a_2=['TAT','TAC','TAA','TAG','CAT','CAC','CAA','CAG','AAT','AAC','AAA','AAG','GAT','GAC','GAA','GAG']
codon_t_2=['TTT','TTC','TTA','TTG','CTT','CTC','CTA','CTG','ATT','ATC','ATA','ATG','GTT','GTC','GTA','GTG']
codon_g_2=['TGT','TGC','TGA','TCG','TGG','CGT','CGC','CGA','CGG','AGT','AGC','AGA','AGG','GGT','GGC','GGA','GGG']
codon_c_2=['TCT','TCC','TCA','TCG','CCT','CCC','CCA','CCG','ACT','ACC','ACA','ACG','GCT','GCC','GCA','GCG']



dna_sub={"A":"C","C":"G","T":"A","G":"T"}
bit_to_dna = {"00": "A", "01": "T", "10": "C", "11": "G"}
dna_to_bit = {v: k for k, v in bit_to_dna.items()}

def xor_16_bit_binary(bin_str1, bin_str2, bin_str3, bin_str4):
    xor_result = "".join(
        str(int(bit1) ^ int(bit2) ^ int(bit3) ^ int(bit4)) 
        for bit1, bit2, bit3, bit4 in zip(bin_str1, bin_str2, bin_str3, bin_str4)
    )
    xor_result_padded = xor_result.zfill(16)
    
    return xor_result

def concatenate_binary(input_list):
    binary_string = ""
    for number in input_list:
        binary_representation = format(number, '04b')
        binary_string += binary_representation
    return binary_string

def find_codon_indexes(elements):
    indexes = []
    for element in elements:
        if element in codon_a_2:
            indexes.append(codon_a_2.index(element))
        elif element in codon_t_2:
            indexes.append(codon_t_2.index(element))
        elif element in codon_g_2:
            indexes.append(codon_g_2.index(element))
        elif element in codon_c_2:
            indexes.append(codon_c_2.index(element))

    return indexes

def substitute_dna_strings(dna_list):  
    substituted_list = []
    for dna_string in dna_list:
        split_chars = list(dna_string)  
        substituted_chars = [dna_sub[char] for char in split_chars]
        substituted_string = ''.join(substituted_chars)
        substituted_list.append(substituted_string)
    
    return substituted_list

def codon_substitution(block_4):
    #print(int(block_4[0],2))
    list1=[]
    list1.append(codon_a[int(block_4[0],2)])
    list1.append(codon_c[int(block_4[1],2)])
    list1.append(codon_g[int(block_4[2],2)])
    if int(block_4[3],2)>(len(codon_t))-1:
        list1.append(codon_t[int(block_4[3],2)%13])#codon_t has only 13 elements, loop over list again to get value
    else:
        list1.append(codon_t[int(block_4[3],2)])
    return list1


def key_generation():
    randbit_int=secrets.randbits(64)
    exact_64_bit = randbit_int | (1 << 63)
    randbit_str=format(exact_64_bit,'b')

    blocks_16=[randbit_str[0:16],randbit_str[16:32],randbit_str[32:48],randbit_str[48:64]]
    block_4_a=[blocks_16[0][0:4],blocks_16[0][4:8],blocks_16[0][8:12],blocks_16[0][12:16]]
    block_4_c=[blocks_16[2][0:4],blocks_16[2][4:8],blocks_16[2][8:12],blocks_16[2][12:16]]
    block_4_d=[blocks_16[3][0:4],blocks_16[3][4:8],blocks_16[3][8:12],blocks_16[3][12:16]]
    block_4_b=[blocks_16[1][0:4],blocks_16[1][4:8],blocks_16[1][8:12],blocks_16[1][12:16]]

    post_sub_a=codon_substitution(block_4_a)
    post_sub_b=codon_substitution(block_4_b)
    post_sub_c=codon_substitution(block_4_c)
    post_sub_d=codon_substitution(block_4_d)

    post_swap_a=substitute_dna_strings(post_sub_a)
    post_swap_b=substitute_dna_strings(post_sub_b)
    post_swap_c=substitute_dna_strings(post_sub_c)
    post_swap_d=substitute_dna_strings(post_sub_d)

    final_a=find_codon_indexes(post_swap_a)
    final_b=find_codon_indexes(post_swap_b)
    final_c=find_codon_indexes(post_swap_c)
    final_d=find_codon_indexes(post_swap_d)

    final_bin_a=concatenate_binary(final_a)
    final_bin_b=concatenate_binary(final_b)
    final_bin_c=concatenate_binary(final_c)
    final_bin_d=concatenate_binary(final_d)

    skey=xor_16_bit_binary(final_bin_a, final_bin_b, final_bin_c, final_bin_d)
    return skey


skey=key_generation()
print(len(skey))



def encrypt_image(image_path, key_str, output_path='encrypted_image.png'):
    # Convert key to 16-bit binary
    key_bin = format(int(key_str, 2), '016b')
    
    # Load and split image
    img = Image.open(image_path)
    img = img.convert("RGB")
    arr = np.array(img)

    # XOR key applied to each pixel channel using 8-bit chunks
    xor_key_r = int(key_bin[:8], 2)
    xor_key_g = int(key_bin[8:], 2)

    # Bitplane Slicing + Reversing bits for obfuscation
    def process_channel(channel, xor_key):
        bitplanes = [(channel >> i) & 1 for i in range(8)]
        bitplanes = bitplanes[::-1]  # Reverse the bitplanes
        reconstructed = sum((bitplanes[i] << i for i in range(8)))
        return np.bitwise_xor(reconstructed, xor_key)

    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

    # Apply processing
    r_enc = process_channel(r, xor_key_r)
    g_enc = process_channel(g, xor_key_g)
    b_enc = process_channel(b, xor_key_r ^ xor_key_g)  # Use combo for Blue

                                    
    encrypted_arr = np.stack([g_enc, b_enc, r_enc], axis=2)

    # Save encrypted image
    encrypted_img = Image.fromarray(encrypted_arr.astype(np.uint8))
    encrypted_img.save(output_path)
    print("Image encrypted and saved as:", output_path)

def decrypt_image(encrypted_path, key_str, output_path='decrypted_image.png'):
    key_bin = format(int(key_str, 2), '016b')
    xor_key_r = int(key_bin[:8], 2)
    xor_key_g = int(key_bin[8:], 2)

    img = Image.open(encrypted_path)
    img = img.convert("RGB")
    arr = np.array(img)

    # Reverse color plane rotation
    g_enc, b_enc, r_enc = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    r_dec = np.bitwise_xor(r_enc, xor_key_r)
    g_dec = np.bitwise_xor(g_enc, xor_key_g)
    b_dec = np.bitwise_xor(b_enc, xor_key_r ^ xor_key_g)

    # Re-reverse bitplanes
    def reverse_process(channel):
        bitplanes = [(channel >> i) & 1 for i in range(8)]
        bitplanes = bitplanes[::-1]
        return sum((bitplanes[i] << i for i in range(8)))

    r = reverse_process(r_dec)
    g = reverse_process(g_dec)
    b = reverse_process(b_dec)

    decrypted_arr = np.stack([r, g, b], axis=2)
    decrypted_img = Image.fromarray(decrypted_arr.astype(np.uint8))
    decrypted_img.save(output_path)
    print("Image decrypted and saved as:", output_path)



key = skey  # 16-bit binary string
encrypt_image("test3.png", key, "enc_test.png")
decrypt_image("enc_test.png", key, "dec_test.png")



def compare_images(original_path, encrypted_path, decrypted_path):
    original = Image.open(original_path)
    original = original.convert("RGB")
    encrypted = Image.open(encrypted_path)
    decrypted = Image.open(decrypted_path)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.title("Original Image")
    plt.imshow(original)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Encrypted Image")
    plt.imshow(encrypted)
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Decrypted Image")
    plt.imshow(decrypted)
    plt.axis("off")

    plt.tight_layout()
    plt.show()


def full_gray_analysis(original_img, encrypted_img, decrypted_img):
    # Ensure all images are in grayscale
    original = original_img.convert("L")  # Convert to grayscale
    encrypted = encrypted_img.convert("L")
    decrypted = decrypted_img.convert("L")

    # Convert to numpy arrays
    original_arr = np.array(original)
    encrypted_arr = np.array(encrypted)
    decrypted_arr = np.array(decrypted)

    # PSNR comparisons (for the entire image)
    psnr_enc = psnr(original_arr, encrypted_arr)
    psnr_dec = psnr(original_arr, decrypted_arr)

    print(f"PSNR (Original vs Encrypted): {psnr_enc:.2f} dB")
    print(f"PSNR (Original vs Decrypted): {psnr_dec:.2f} dB")



compare_images("test3.png", "enc_test.png", "dec_test.png")
original_img = Image.open("test3.png")
encrypted_img = Image.open("enc_test.png")
decrypted_img = Image.open("dec_test.png")
full_gray_analysis(original_img, encrypted_img,decrypted_img)