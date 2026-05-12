# Copyright (c) 2023, The Synthesis Engineers
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Generates exponential backoff schedules for retries."""

from typing import List

def _validate_inputs(attempts: int, base_seconds: int, cap_seconds: int) -> None:
    """Checks if the schedule parameters are valid, raising ValueError otherwise."""
    if not isinstance(attempts, int) or attempts < 0:
        raise ValueError("attempts must be a non-negative integer.")
    if not isinstance(base_seconds, int) or base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer.")
    if not isinstance(cap_seconds, int) or cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer.")


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> List[int]:
    """
    Builds a list of delays for an exponential backoff retry strategy.

    The delay for attempt `i` (0-indexed) is calculated as:
    `min(base_seconds * (2**i), cap_seconds)`

    Args:
        attempts: The number of retry attempts to schedule. Must be >= 0.
        base_seconds: The base delay for the first attempt. Must be > 0.
        cap_seconds: The maximum delay for any attempt. Must be > 0.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        The list will be empty if attempts is 0.

    Raises:
        ValueError: If any of the input parameters are invalid.
    """
    _validate_inputs(attempts, base_seconds, cap_seconds)

    # A list comprehension is a direct and readable way to generate the schedule.
    # The general case of the list comprehension correctly handles the special
    # case of `attempts=0` by producing an empty list.
    # The expression `1 << i` is an efficient way to calculate 2**i.
    return [
        min(base_seconds * (1 << i), cap_seconds) for i in range(attempts)
    ]
