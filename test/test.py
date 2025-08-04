import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from tqv import TinyQV

#Test Configuration
PERIPHERAL_NUM = 16

#Register Map
REG_Q_READ      = 0x00 # Address to read the LFSR state
REG_Q_SHIFT_CMD = 0x00 # Address to trigger a SHIFT command
REG_Q_LOAD_CMD  = 0x01 # Address to trigger a LOAD command
RESET_VALUE     = 0xAA # The expected value of the LFSR after reset
TEST_SEED       = 0x14 # A seed value to use for testing (20 decimal)


# LFSR golden model 
def lfsr_model(current_value: int) -> int:
    """
    A perfect software model of the DUT's LFSR logic.
    It calculates the next state based on the current state.
    Matches Verilog: `feedback = q[7]^q[5]^q[4]^q[3]` and `q <= {q[6:0], feedback}`
    """
    feedback = ((current_value >> 7) & 1) ^ \
               ((current_value >> 5) & 1) ^ \
               ((current_value >> 4) & 1) ^ \
               ((current_value >> 3) & 1)
    
    next_value = ((current_value << 1) | feedback) & 0xFF
    return next_value


async def setup_dut(dut):
    """Initializes the DUT and starts the clock."""
    # Start the clock
    clock = Clock(dut.clk, 100, units="ns") # 10 MHz
    cocotb.start_soon(clock.start())

    tqv = TinyQV(dut, PERIPHERAL_NUM)
    await tqv.reset()
    return tqv

@cocotb.test()
async def test_reset(dut):
    """Tests that the LFSR register resets to the correct default value."""
    dut._log.info("////////////// Starting Reset Test ///////////////")
    tqv = await setup_dut(dut)

    val = await tqv.read_reg(REG_Q_READ)
    
    assert val == RESET_VALUE, f"Reset failed! Expected 0x{RESET_VALUE:02X}, got 0x{val:02X}"
    dut._log.info(f"Reset value verified: 0x{val:02X}")


@cocotb.test()
async def test_load(dut):
    """Tests that a new seed value can be loaded into the LFSR."""
    dut._log.info("////////////// Starting Load Test ///////////////")
    tqv = await setup_dut(dut)

    # Write the test seed value to the LOAD command address
    await tqv.write_reg(REG_Q_LOAD_CMD, TEST_SEED)
    
    # Read the value back to verify the write was successful
    val = await tqv.read_reg(REG_Q_READ)
    assert val == TEST_SEED, f"Failed to load value! Expected 0x{TEST_SEED:02X}, got 0x{val:02X}"
    dut._log.info(f"✅ Successfully loaded value 0x{val:02X}.")


@cocotb.test()
async def test_sequence(dut):
    """Tests that the LFSR shifts through a sequence of values correctly."""
    dut._log.info("////////////// Starting Sequence Test ///////////////")
    tqv = await setup_dut(dut)

    # Start from a known state by loading our test seed
    await tqv.write_reg(REG_Q_LOAD_CMD, TEST_SEED)
    current_lfsr_val = await tqv.read_reg(REG_Q_READ)

    dut._log.info(f"Starting sequence from seed 0x{current_lfsr_val:02X}...")
    for i in range(50):
        expected_next_state = lfsr_model(current_lfsr_val)

        # Trigger a single shift in the hardware. The data (0) is ignored.
        await tqv.write_reg(REG_Q_SHIFT_CMD, 0)
        
        # Read the new value from the hardware
        actual_next_state = await tqv.read_reg(REG_Q_READ)
        
        # Assert that the hardware's output matches the model's prediction
        assert actual_next_state == expected_next_state, \
            f"Sequence mismatch on cycle {i+1}! Expected 0x{expected_next_state:02X}, got 0x{actual_next_state:02X}"
        
        # Update our local variable for the next loop iteration
        current_lfsr_val = actual_next_state
    
    dut._log.info(f"LFSR sequence verified for 50 cycles.")
    dut._log.info("///////// All tests passed!//////////////")