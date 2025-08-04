 /*
 * Copyright (c) 2025 Ayush Dixit
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

 module tqvp_rng (
    input         clk,          // Clock - the TinyQV project clock is normally set to 64MHz.
    input         rst_n,        // Reset_n - low to reset.

    input  [7:0]  ui_in,        // The input PMOD, always available.  Note that ui_in[7] is normally used for UART RX.
                                // The inputs are synchronized to the clock, note this will introduce 2 cycles of delay on the inputs.

    output [7:0]  uo_out,       // The output PMOD.  Each wire is only connected if this peripheral is selected.
                                // Note that uo_out[0] is normally used for UART TX.

    input [3:0]   address,      // Address within this peripheral's address space

    input         data_write,   // Data write request from the TinyQV core.
    input [7:0]   data_in,      // Data in to the peripheral, valid when data_write is high.
    
    output [7:0]  data_out      // Data out from the peripheral, set this in accordance with the supplied address
);

      reg [7:0] q ; 

      wire feedback ;
      assign feedback = q[7] ^ q[5] ^ q[4] ^ q[3];


      always @(posedge clk) begin
          if (!rst_n) begin
              q <= 8'hAA;
          end else begin
              if (data_write) begin
                  if (address == 4'h0) begin
                      // Address 0: SHIFT the LFSR
                      q <= {q[6:0], feedback};
                  end else if (address == 4'h1) begin
                      // Address 1: LOAD the LFSR with a new value
                      q <= data_in;
                  end
              end
          end
      end
 
     assign uo_out  = q ; 
  
     assign data_out = (address == 4'h0) ? q : 8'h0;

endmodule