# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messaging.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fmessaging.proto\"\x07\n\x05\x45mpty\"!\n\x0eMessageRequest\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"!\n\x0fMessageResponse\x12\x0e\n\x06result\x18\x01 \x01(\t2F\n\x10MessagingService\x12\x32\n\rtextMessaging\x12\x0f.MessageRequest\x1a\x10.MessageResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'messaging_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EMPTY']._serialized_start=19
  _globals['_EMPTY']._serialized_end=26
  _globals['_MESSAGEREQUEST']._serialized_start=28
  _globals['_MESSAGEREQUEST']._serialized_end=61
  _globals['_MESSAGERESPONSE']._serialized_start=63
  _globals['_MESSAGERESPONSE']._serialized_end=96
  _globals['_MESSAGINGSERVICE']._serialized_start=98
  _globals['_MESSAGINGSERVICE']._serialized_end=168
# @@protoc_insertion_point(module_scope)
