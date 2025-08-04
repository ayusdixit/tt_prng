<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

The peripheral index is the number TinyQV will use to select your peripheral.  You will pick a free
slot when raising the pull request against the main TinyQV repository, and can fill this in then.  You
also need to set this value as the PERIPHERAL_NUM in your test script.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

# 8-bit Linear Feedback Shift Register Random Number Generator (LFSR PRNG)

Author: Ayush Dixit


## What it does

This peripheral implements an 8-bit **Linear Feedback Shift Register (LFSR)** that generates a pseudo-random sequence of numbers. The generator is a "Fibonacci" LFSR using a fixed polynomial to produce a repeatable sequence of values, which is useful for simulations, procedural generation, or basic test patterns.

The state of the PRNG can be both read from and written to, allowing it to be seeded with a specific starting value. Advancing the PRNG to its next state is triggered by a command sent via the register interface.

Key features include:
- **Type**: 8-bit Fibonacci LFSR (Left Shift)
- **Polynomial**: `x^8 + x^5 + x^4 + x^3 + 1` (Taps at bits 7, 5, 4, 3)
- **Seeding**: The LFSR can be set to any 8-bit value to control the starting point of the sequence.
- **Stepping**: The LFSR state is advanced one step at a time via a command, giving the user full control over the sequence generation.

## Register map

This peripheral uses a **command-based interface** where writing to a specific address triggers an action rather than storing a value in a traditional register.

| Address | Write Action             | Read Action               | Description                                                                 |
|---------|--------------------------|---------------------------|-----------------------------------------------------------------------------|
| `0x00`  | **SHIFT Command**        | Read current LFSR state   | Writing any data to this address causes the LFSR to advance to its next state. Reading this address returns the current 8-bit value of the LFSR.|
| `0x01`  | **LOAD Command**         | *(Returns 0)*             | Writing data to this address loads that 8-bit value directly into the LFSR, seeding the generator. |

## How to test

 do make -B
## External hardware
 