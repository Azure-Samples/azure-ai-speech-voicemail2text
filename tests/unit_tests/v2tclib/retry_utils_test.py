#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from unittest.mock import patch, MagicMock, call
import os, sys
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib.retry_utils import before_callback_log, after_callback_log, RetryCallState, retry_with_custom_strategy, retry_wait_config

def custom_side_effect(config_base, property_name, literal_eval=False):
    if property_name == 'retry_on_exception':
        return config_base.get('retry_on_exception')
    elif property_name == 'retry_max_attempts':
        return config_base.get('retry_max_attempts')
    elif property_name == 'retry_wait_exponential_backoff':
        return config_base.get('retry_wait_exponential_backoff')
        
# Test with a function that always raises an exception
def always_raise():
    raise Exception("Test exception")      

@patch('v2ticlib.retry_utils.log')
def test_before_callback_log(mock_log):
    # Create a mock RetryCallState object with attempt_number = 1
    mock_retry_state = MagicMock(spec=RetryCallState)
    mock_retry_state.attempt_number = 1

    # Call the before_callback_log function with the mock RetryCallState object
    result = before_callback_log(mock_retry_state)

    # Assert that the function returns None (since is_first_attempt should return True for attempt_number = 1)
    assert result is None

    # Create a mock RetryCallState object with attempt_number > 1
    mock_retry_state = MagicMock(spec=RetryCallState)
    mock_retry_state.attempt_number = 2
    mock_retry_state.log = mock_log

    # Call the before_callback_log function with the mock RetryCallState object
    result = before_callback_log(mock_retry_state)

    # Assert that the function logs the correct message
    #retry attempt is one less than attempt number to account for the first attempt
    mock_retry_state.log.assert_called_once_with("Attempting retry 1 ...")

def test_after_callback_log():
    mock_retry_state = MagicMock(spec=RetryCallState)
    # Test with a RetryCallState object with attempt_number = 1
    mock_retry_state.attempt_number = 1

    # Call the after_callback_log function with the mock RetryCallState object
    result = after_callback_log(mock_retry_state)

    # Assert that the function returns None (since is_first_attempt should return True for attempt_number = 1)
    assert result is None
    
    # Create a mock RetryCallState object with attempt_number > 1
    with patch('v2ticlib.retry_utils.log') as mock_log:
        mock_retry_state.attempt_number = 2
        after_callback_log(mock_retry_state)
        #retry attempt is one less than attempt number to account for the first attempt
        mock_log.assert_called_once_with("Retry failed on attempt 1")

    # Test with a RetryCallState object with attempt_number = 4
    with patch('v2ticlib.retry_utils.log') as mock_log:
        mock_retry_state.attempt_number = 4
        after_callback_log(mock_retry_state)
        #retry attempt is one less than attempt number to account for the first attempt
        mock_log.assert_called_once_with("Retry failed on attempt 3")

#Test case when ${max_attempts} = length(wait_exponential_backoff) with retry exception as Exception
@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy(mock_get_property):   
    # Test with a config_base that retries 3 times with exponential backoff 0.5 sec, 1 sec and 2 sec
    config_base = {        
        "retry_max_attempts": 3,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "Exception"
    }
            
    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(always_raise)()
        except Exception as e:
            print(e)

        # Assert that the function logs the correct messages
        mock_log.assert_has_calls([
            call("Attempting retry 1 ..."),
            call("Retry failed on attempt 1"),
            call("Attempting retry 2 ..."),
            call("Retry failed on attempt 2"),
            call("Attempting retry 3 ..."),
            call("Retry failed on attempt 3")
        ])

@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy_with_child_exception(mock_get_property):    
    # Test with a config_base that retries 3 times with exponential backoff 0.5 sec, 1 sec and 2 sec
    config_base = {        
        "retry_max_attempts": 3,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "Exception"
    }
    
    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(always_raise)()
        except Exception as e:
            print(e)
        
        # Assert that the function logs the correct messages
        mock_log.assert_has_calls([
            call("Attempting retry 1 ..."),
            call("Retry failed on attempt 1"),
            call("Attempting retry 2 ..."),
            call("Retry failed on attempt 2"),
            call("Attempting retry 3 ..."),
            call("Retry failed on attempt 3")
        ])
                
@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy_with_one_attempt(mock_get_property):
    # Test with a function that always raises an exception
    counter = 0
    def raise_once():
        nonlocal counter
        if counter == 0:
            counter += 1
            raise Exception("Test exception")
        return
    
    # Test with a config_base that retries 3 times with exponential backoff 0.5 sec, 1 sec and 2 sec
    config_base = {        
        "retry_max_attempts": 3,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "Exception"
    }

    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(raise_once)()
        except Exception as e:
            print(e)

        # Assert that the function logs the correct messages
        mock_log.assert_has_calls([
            call("Attempting retry 1 ...")
        ])
        
@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy_with_more_attempts(mock_get_property):
    # Test with a function that always raises an exception
    counter = 0
    def raise_twice():
        nonlocal counter
        if counter < 2:
            counter += 1
            raise Exception("Test exception")
        return
    
    # Test with a config_base that retries 3 times with exponential backoff 0.5 sec, 1 sec and 2 sec
    config_base = {        
        "retry_max_attempts": 3,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "Exception"
    }
    
    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(raise_twice)()
        except Exception as e:
            print(e)

        # Assert that the function logs the correct messages
        mock_log.assert_has_calls([
            call("Attempting retry 1 ..."),
            call("Retry failed on attempt 1"),
            call("Attempting retry 2 ...")
        ])
        
@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy_with_no_attempts(mock_get_property):    
    # Test with a config_base that retries 0 times with exponential backoff 0.5 sec, 1 sec and 2 sec
    config_base = {        
        "retry_max_attempts": 0,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "Exception"
    }

    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(always_raise)()
        except Exception as e:
            print(e)

        # Assert that the function logs the correct messages
        mock_log.assert_not_called()
        
@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy_with_no_attempts_with_value_negative(mock_get_property):    
    # Test with a config_base that retries -1 times with exponential backoff 0.5 sec, 1 sec and 2 sec
    config_base = {        
        "retry_max_attempts": -1,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "Exception"
    }

    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(always_raise)()
        except Exception as e:
            print(e)

        # Assert that the function logs the correct messages
        mock_log.assert_not_called()

@patch('v2ticlib.retry_utils.get_property')
def test_retry_with_custom_strategy_with_mismatching_exception(mock_get_property):    
    # Test with a config_base that retries 3 times with exponential backoff 0.5 sec, 1 sec and 2 sec for OSError
    config_base = {        
        "retry_max_attempts": 3,
        "retry_wait_exponential_backoff": [0.5, 1, 2],
        "retry_on_exception": "OSError"
    }

    # Call the retry_with_custom_strategy function with the always_raise function and the config_base
    with patch('v2ticlib.retry_utils.log') as mock_log:
        try:
            mock_get_property.side_effect = custom_side_effect
            retry_with_custom_strategy(config_base)(always_raise)()
        except Exception as e:
            print(e)

        # Assert that the function logs the correct messages
        mock_log.assert_not_called()

@patch('v2ticlib.retry_utils.get_retry_max_attempts')
@patch('v2ticlib.retry_utils.get_retry_wait_exp_backoff')
@patch('v2ticlib.retry_utils.wait_fixed')
@patch('v2ticlib.retry_utils.wait_chain')
def test_retry_wait_config(mock_wait_chain, mock_wait_fixed, mock_get_retry_wait_exp_backoff, mock_get_retry_max_attempts):
    # Test case 1(A): max_attempts < 1
    mock_get_retry_max_attempts.return_value = 0
    assert retry_wait_config({}) is None
    
    # Test case 1(B): max_attempts is negative
    mock_get_retry_max_attempts.return_value = -1
    assert retry_wait_config({}) is None

    # Test case 2: exponential_backoff is None
    mock_get_retry_max_attempts.return_value = 3
    mock_get_retry_wait_exp_backoff.return_value = None
    assert retry_wait_config({}) is None

    # Test case 3: exponential_backoff is empty
    mock_get_retry_wait_exp_backoff.return_value = []
    assert retry_wait_config({}) is None

    mock_get_retry_wait_exp_backoff.return_value = [0.5, 1, 2]
    
    # Test case 4: ${max_attempts} < length(wait_exponential_backoff)
    mock_get_retry_max_attempts.return_value = 1
    mock_wait_fixed.return_value = MagicMock()
    assert retry_wait_config({}) == mock_wait_chain.return_value
    mock_wait_fixed.assert_called_once_with(0.5)
    mock_wait_chain.assert_called_once_with(mock_wait_fixed.return_value)

    mock_wait_chain.reset_mock()
    mock_wait_fixed.reset_mock()
    
    # Test case 5: ${max_attempts} = length(wait_exponential_backoff)
    mock_get_retry_max_attempts.return_value = 3
    mock_wait_fixed.return_value = MagicMock()
    assert retry_wait_config({}) == mock_wait_chain.return_value
    mock_wait_fixed.assert_has_calls
    (
        [
            call(0.5), call(1), call(2)
        ]
    )
    mock_wait_chain.assert_called_once_with(mock_wait_fixed.return_value, mock_wait_fixed.return_value, mock_wait_fixed.return_value)

    mock_wait_chain.reset_mock()
    mock_wait_fixed.reset_mock()
    
    # Test case 6: ${max_attempts} > length(wait_exponential_backoff)
    mock_get_retry_max_attempts.return_value = 5
    assert retry_wait_config({}) == mock_wait_chain.return_value
    mock_wait_fixed.assert_has_calls
    (
        [
            call(0.5), call(1), call(2), call(2), call(2)
        ]
    )
    mock_wait_chain.assert_called_once_with(mock_wait_fixed.return_value, mock_wait_fixed.return_value, mock_wait_fixed.return_value, mock_wait_fixed.return_value, mock_wait_fixed.return_value)
