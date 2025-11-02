"""
Voice and Calling System v15 - Termux-API Integration
Complete voice interaction and calling capabilities using Android Termux-API
Natural language voice commands, text-to-speech, speech-to-text, and contact management
"""

import os
import json
import time
import asyncio
import logging
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
import aiofiles

@dataclass
class Contact:
    """Contact information"""
    name: str
    phone_number: str
    email: Optional[str] = None
    last_called: Optional[datetime] = None
    call_count: int = 0

@dataclass
class VoiceCommand:
    """Voice command structure"""
    command_text: str
    confidence: float
    intent: str
    parameters: Dict[str, Any]
    timestamp: datetime

@dataclass
class CallRecord:
    """Call record"""
    contact_name: str
    phone_number: str
    call_type: str  # incoming, outgoing, missed
    duration: int  # seconds
    timestamp: datetime

class VoiceCallingSystemV15:
    """
    Voice and Calling System with Termux-API Integration

    Features:
    - Text-to-speech via Termux-API
    - Speech-to-text via Termux-API
    - Voice command processing
    - Contact management
    - Voice calling (dialing)
    - SMS messaging
    - Call history and logging
    - Natural language understanding
    - Multi-language support
    """

    def __init__(self, termux_controller, config: Dict[str, Any], logger: logging.Logger):
        self.termux_controller = termux_controller
        self.config = config
        self.logger = logger

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data" / "voice_calling"
        self.contacts_path = self.data_path / "contacts"
        self.call_history_path = self.data_path / "call_history"
        self.voice_commands_path = self.data_path / "voice_commands"

        # Create directories
        for path in [self.data_path, self.contacts_path, self.call_history_path, self.voice_commands_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Voice settings
        self.voice_enabled = config.get('enabled', True)
        self.language = config.get('language', 'en-US')
        self.speech_rate = config.get('speed', 1.0)
        self.pitch = config.get('pitch', 1.0)

        # System state
        self.voice_mode_active = False
        self.calling_enabled = False
        self.contacts = {}
        self.call_history = []
        self.voice_commands = []

        # Voice command patterns
        self.command_patterns = self._initialize_command_patterns()

        # Call management
        self.active_call = None
        self.call_in_progress = False

        # Audio settings
        self.tts_engine = "termux"  # Use Termux TTS
        self.stt_engine = "termux"  # Use Termux STT

    async def initialize(self):
        """Initialize voice and calling system"""
        try:
            # Check Termux-API availability
            if not await self._check_termux_api():
                self.logger.warning("⚠️ Termux-API not found, voice features will be limited")
                self.voice_enabled = False

            # Load contacts
            await self._load_contacts()

            # Load call history
            await self._load_call_history()

            # Initialize voice command processing
            await self._initialize_voice_commands()

            self.logger.info("✅ Voice and Calling System v15 initialized")

        except Exception as e:
            self.logger.error(f"❌ Voice and Calling System initialization failed: {e}")
            raise

    async def _check_termux_api(self) -> bool:
        """Check if Termux-API is available"""
        try:
            # Check if termux-api command exists
            result = subprocess.run(
                ['which', 'termux-api'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    async def _load_contacts(self):
        """Load contacts from file or Android contacts"""
        try:
            contacts_file = self.contacts_path / "contacts.json"

            if contacts_file.exists():
                async with aiofiles.open(contacts_file, 'r') as f:
                    data = json.loads(await f.read())
                    for name, contact_data in data.items():
                        self.contacts[name] = Contact(**contact_data)
            else:
                # Try to load from Android contacts
                await self._load_android_contacts()

            self.logger.info(f"📱 Loaded {len(self.contacts)} contacts")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load contacts: {e}")
            self.contacts = {}

    async def _load_android_contacts(self):
        """Load contacts from Android using Termux-API"""
        try:
            if await self._check_termux_api():
                # Get contacts using Termux-API
                result = subprocess.run(
                    ['termux-contact-list'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    contacts_data = json.loads(result.stdout)

                    for contact in contacts_data:
                        name = contact.get('name', '')
                        number = contact.get('number', '')

                        if name and number:
                            self.contacts[name] = Contact(
                                name=name,
                                phone_number=number,
                                email=contact.get('email')
                            )

                    await self._save_contacts()
                    self.logger.info(f"✅ Loaded {len(self.contacts)} contacts from Android")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load Android contacts: {e}")

    async def _save_contacts(self):
        """Save contacts to file"""
        try:
            contacts_file = self.contacts_path / "contacts.json"
            data = {name: asdict(contact) for name, contact in self.contacts.items()}

            async with aiofiles.open(contacts_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save contacts: {e}")

    async def _load_call_history(self):
        """Load call history"""
        try:
            history_file = self.call_history_path / "call_history.json"

            if history_file.exists():
                async with aiofiles.open(history_file, 'r') as f:
                    data = json.loads(await f.read())
                    self.call_history = [CallRecord(**record) for record in data.get('calls', [])]

            self.logger.info(f"📞 Loaded {len(self.call_history)} call records")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load call history: {e}")
            self.call_history = []

    async def _save_call_history(self):
        """Save call history"""
        try:
            history_file = self.call_history_path / "call_history.json"
            data = {
                'calls': [asdict(record) for record in self.call_history[-100:]],  # Keep last 100
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save call history: {e}")

    async def _initialize_voice_commands(self):
        """Initialize voice command patterns"""
        self.command_patterns = {
            'call': [
                r'call\s+(.+)',
                r'dial\s+(.+)',
                r'phone\s+(.+)'
            ],
            'message': [
                r'send\s+message\s+to\s+(.+)',
                r'text\s+(.+)',
                r'sms\s+(.+)'
            ],
            'search': [
                r'search\s+(.+)',
                r'find\s+(.+)',
                'look\s+for\s+(.+)'
            ],
            'help': [
                r'help',
                r'what\s+can\s+you\s+do',
                r'commands'
            ],
            'status': [
                r'status',
                r'how\s+are\s+you',
                r'what\'s\s+your\s+status'
            ],
            'stop': [
                r'stop',
                r'cancel',
                r'end'
            ]
        }

    def _initialize_command_patterns(self) -> Dict[str, List[str]]:
        """Initialize voice command patterns"""
        return {
            'call': [
                r'call\s+(.+)',
                r'dial\s+(.+)',
                r'phone\s+(.+)'
            ],
            'message': [
                r'send\s+message\s+to\s+(.+)',
                r'text\s+(.+)',
                r'sms\s+(.+)'
            ],
            'add_contact': [
                r'add\s+contact\s+(.+)',
                r'new\s+contact\s+(.+)'
            ],
            'search_contact': [
                r'find\s+contact\s+(.+)',
                r'search\s+contact\s+(.+)'
            ],
            'help': [
                r'help',
                r'what\s+can\s+you\s+do',
                r'commands'
            ],
            'status': [
                r'status',
                r'how\s+are\s+you'
            ]
        }

    async def enable_voice_mode(self):
        """Enable voice interaction mode"""
        try:
            if not self.voice_enabled:
                await self.speak("Voice features are not available. Termux-API is required.")
                return False

            self.voice_mode_active = True
            await self.speak("Voice mode enabled. You can now speak commands to JARVIS.")
            self.logger.info("🎤 Voice mode enabled")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to enable voice mode: {e}")
            return False

    async def disable_voice_mode(self):
        """Disable voice interaction mode"""
        try:
            self.voice_mode_active = False
            if self.voice_enabled:
                await self.speak("Voice mode disabled.")
            self.logger.info("🔇 Voice mode disabled")

        except Exception as e:
            self.logger.error(f"❌ Failed to disable voice mode: {e}")

    async def enable_calling(self):
        """Enable calling capabilities"""
        try:
            if not await self._check_termux_api():
                await self.speak("Calling features are not available. Termux-API is required.")
                return False

            self.calling_enabled = True
            await self.speak("Calling features enabled. You can now make calls and send messages.")
            self.logger.info("📞 Calling features enabled")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to enable calling: {e}")
            return False

    async def speak(self, text: str) -> bool:
        """Text-to-speech using Termux-API"""
        try:
            if not self.voice_enabled:
                self.logger.info(f"🗣️ TTS (disabled): {text}")
                return True

            # Use Termux TTS
            command = [
                'termux-tts-speak',
                '-l', self.language,
                '-r', str(self.speech_rate),
                '-p', str(self.pitch),
                text
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info(f"🗣️ Spoke: {text}")
                return True
            else:
                self.logger.error(f"❌ TTS failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ TTS timeout")
            return False
        except Exception as e:
            self.logger.error(f"❌ TTS error: {e}")
            return False

    async def listen(self) -> Optional[str]:
        """Speech-to-text using Termux-API"""
        try:
            if not self.voice_enabled:
                self.logger.warning("⚠️ Speech recognition not available")
                return None

            # Use Termux STT
            command = [
                'termux-speech-to-text',
                '-l', self.language
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse STT result
                stt_data = json.loads(result.stdout)
                text = stt_data.get('text', '')

                if text:
                    self.logger.info(f"🎤 Heard: {text}")
                    return text
                else:
                    self.logger.info("🎤 No speech detected")
                    return None
            else:
                self.logger.error(f"❌ STT failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.info("🎤 Listening timeout")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ STT JSON decode error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ STT error: {e}")
            return None

    async def process_voice_command(self, command_text: str) -> Optional[VoiceCommand]:
        """Process voice command and extract intent"""
        try:
            command_text = command_text.strip().lower()

            # Match command patterns
            for intent, patterns in self.command_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, command_text, re.IGNORECASE)
                    if match:
                        parameters = {}
                        if match.groups():
                            parameters['target'] = match.group(1).strip()

                        voice_command = VoiceCommand(
                            command_text=command_text,
                            confidence=0.9,  # High confidence for regex matches
                            intent=intent,
                            parameters=parameters,
                            timestamp=datetime.now()
                        )

                        self.voice_commands.append(voice_command)
                        await self._save_voice_commands()

                        return voice_command

            # No pattern matched
            return VoiceCommand(
                command_text=command_text,
                confidence=0.1,
                intent='unknown',
                parameters={},
                timestamp=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"❌ Voice command processing failed: {e}")
            return None

    async def execute_voice_command(self, command: VoiceCommand) -> str:
        """Execute voice command"""
        try:
            intent = command.intent
            parameters = command.parameters

            if intent == 'call':
                return await self._handle_call_command(parameters)
            elif intent == 'message':
                return await self._handle_message_command(parameters)
            elif intent == 'add_contact':
                return await self._handle_add_contact_command(parameters)
            elif intent == 'search_contact':
                return await self._handle_search_contact_command(parameters)
            elif intent == 'help':
                return await self._handle_help_command()
            elif intent == 'status':
                return await self._handle_status_command()
            elif intent == 'unknown':
                return await self.speak("I didn't understand that command. Please try again.")
            else:
                return await self.speak(f"Command {intent} is not implemented yet.")

        except Exception as e:
            self.logger.error(f"❌ Voice command execution failed: {e}")
            await self.speak("Sorry, I encountered an error while executing your command.")
            return f"Error: {e}"

    async def _handle_call_command(self, parameters: Dict[str, Any]) -> str:
        """Handle call command"""
        try:
            target = parameters.get('target', '')
            if not target:
                await self.speak("Who would you like to call?")
                return "Please specify a contact name or phone number"

            # Find contact
            contact = await self._find_contact(target)
            if not contact:
                await self.speak(f"I couldn't find a contact named {target}")
                return f"Contact not found: {target}"

            # Make call
            success = await self.make_call(contact.phone_number, contact.name)
            if success:
                await self.speak(f"Calling {contact.name}")
                return f"Calling {contact.name} at {contact.phone_number}"
            else:
                await self.speak("Failed to make the call")
                return "Call failed"

        except Exception as e:
            self.logger.error(f"❌ Call command failed: {e}")
            await self.speak("Sorry, I failed to make the call")
            return f"Call command error: {e}"

    async def _handle_message_command(self, parameters: Dict[str, Any]) -> str:
        """Handle message command"""
        try:
            target = parameters.get('target', '')
            if not target:
                await self.speak("Who would you like to message?")
                return "Please specify a contact name"

            # Find contact
            contact = await self._find_contact(target)
            if not contact:
                await self.speak(f"I couldn't find a contact named {target}")
                return f"Contact not found: {target}"

            await self.speak(f"What message would you like to send to {contact.name}?")

            # Listen for message content
            message_text = await self.listen()
            if not message_text:
                await self.speak("I didn't catch that. Please try again.")
                return "No message detected"

            # Send message
            success = await self.send_message(contact.phone_number, message_text)
            if success:
                await self.speak(f"Message sent to {contact.name}")
                return f"Message sent to {contact.name}"
            else:
                await self.speak("Failed to send the message")
                return "Message failed"

        except Exception as e:
            self.logger.error(f"❌ Message command failed: {e}")
            await self.speak("Sorry, I failed to send the message")
            return f"Message command error: {e}"

    async def _handle_add_contact_command(self, parameters: Dict[str, Any]) -> str:
        """Handle add contact command"""
        try:
            target = parameters.get('target', '')
            if not target:
                await self.speak("What's the contact's name?")
                return "Please specify a contact name"

            # Get phone number
            await self.speak(f"What's {target}'s phone number?")
            phone_number = await self.listen()
            if not phone_number:
                await self.speak("I didn't catch the phone number")
                return "No phone number detected"

            # Clean phone number
            phone_number = re.sub(r'[^\d+]', '', phone_number)

            # Add contact
            await self.add_contact(target, phone_number)
            await self.speak(f"Contact {target} added successfully")
            return f"Contact {target} added with phone number {phone_number}"

        except Exception as e:
            self.logger.error(f"❌ Add contact command failed: {e}")
            await self.speak("Sorry, I failed to add the contact")
            return f"Add contact error: {e}"

    async def _handle_search_contact_command(self, parameters: Dict[str, Any]) -> str:
        """Handle search contact command"""
        try:
            target = parameters.get('target', '')
            if not target:
                await self.speak("Who are you looking for?")
                return "Please specify a contact name"

            # Search contacts
            matches = await self.search_contacts(target)
            if matches:
                names = [contact.name for contact in matches[:5]]  # Limit to 5 results
                await self.speak(f"Found {len(matches)} contacts: {', '.join(names)}")
                return f"Found contacts: {', '.join(names)}"
            else:
                await self.speak(f"No contacts found for {target}")
                return f"No contacts found: {target}"

        except Exception as e:
            self.logger.error(f"❌ Search contact command failed: {e}")
            await self.speak("Sorry, I failed to search contacts")
            return f"Search contact error: {e}"

    async def _handle_help_command(self) -> str:
        """Handle help command"""
        help_text = """
I can help you with the following voice commands:

• Call [contact name] - Make a phone call
• Send message to [contact name] - Send a text message
• Add contact [name] - Add a new contact
• Find contact [name] - Search for contacts
• Status - Check system status
• Help - Show this help message
• Stop - Stop voice interaction

Just say "Hey JARVIS" followed by your command!
        """
        await self.speak("I can help you make calls, send messages, manage contacts, and more. Say help to hear all available commands.")
        return "Voice help provided"

    async def _handle_status_command(self) -> str:
        """Handle status command"""
        status = f"""
JARVIS Voice System Status:
• Voice Mode: {'Active' if self.voice_mode_active else 'Inactive'}
• Calling: {'Enabled' if self.calling_enabled else 'Disabled'}
• Contacts: {len(self.contacts)} contacts loaded
• Call History: {len(self.call_history)} records
        """
        await self.speak(f"Voice system is {'active' if self.voice_mode_active else 'inactive'}. I have {len(self.contacts)} contacts saved.")
        return status.strip()

    async def make_call(self, phone_number: str, contact_name: str = "") -> bool:
        """Make a phone call using Termux-API"""
        try:
            if not self.calling_enabled:
                self.logger.warning("⚠️ Calling not enabled")
                return False

            # Use Termux telephony API
            command = ['termux-telephony-call', phone_number]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.call_in_progress = True
                self.active_call = {
                    'phone_number': phone_number,
                    'contact_name': contact_name,
                    'start_time': datetime.now()
                }

                # Create call record
                call_record = CallRecord(
                    contact_name=contact_name or phone_number,
                    phone_number=phone_number,
                    call_type='outgoing',
                    duration=0,  # Will be updated when call ends
                    timestamp=datetime.now()
                )

                self.call_history.append(call_record)
                await self._save_call_history()

                self.logger.info(f"📞 Call initiated: {contact_name} at {phone_number}")
                return True
            else:
                self.logger.error(f"❌ Call failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Call timeout")
            return False
        except Exception as e:
            self.logger.error(f"❌ Call error: {e}")
            return False

    async def send_message(self, phone_number: str, message: str) -> bool:
        """Send SMS message using Termux-API"""
        try:
            if not self.calling_enabled:
                self.logger.warning("⚠️ Calling not enabled")
                return False

            # Use Termux SMS API
            command = ['termux-sms-send', '-n', phone_number, message]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info(f"📱 Message sent to {phone_number}: {message}")
                return True
            else:
                self.logger.error(f"❌ Message failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Message timeout")
            return False
        except Exception as e:
            self.logger.error(f"❌ Message error: {e}")
            return False

    async def add_contact(self, name: str, phone_number: str, email: str = None):
        """Add new contact"""
        try:
            contact = Contact(
                name=name,
                phone_number=phone_number,
                email=email
            )

            self.contacts[name] = contact
            await self._save_contacts()

            self.logger.info(f"👤 Contact added: {name} - {phone_number}")

        except Exception as e:
            self.logger.error(f"❌ Failed to add contact: {e}")

    async def _find_contact(self, name: str) -> Optional[Contact]:
        """Find contact by name"""
        try:
            # Exact match first
            if name in self.contacts:
                return self.contacts[name]

            # Partial match
            for contact_name, contact in self.contacts.items():
                if name.lower() in contact_name.lower() or contact_name.lower() in name.lower():
                    return contact

            return None

        except Exception as e:
            self.logger.error(f"❌ Contact search failed: {e}")
            return None

    async def search_contacts(self, query: str) -> List[Contact]:
        """Search contacts by name or phone number"""
        try:
            query = query.lower()
            matches = []

            for contact in self.contacts.values():
                if (query in contact.name.lower() or
                    query in contact.phone_number or
                    (contact.email and query in contact.email.lower())):
                    matches.append(contact)

            return matches

        except Exception as e:
            self.logger.error(f"❌ Contact search failed: {e}")
            return []

    async def _save_voice_commands(self):
        """Save voice commands history"""
        try:
            commands_file = self.voice_commands_path / "voice_commands.json"
            data = {
                'commands': [asdict(cmd) for cmd in self.voice_commands[-50:]],  # Keep last 50
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(commands_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save voice commands: {e}")

    async def start_voice_interaction_loop(self):
        """Start continuous voice interaction loop"""
        try:
            await self.speak("Voice interaction started. Say 'Hey JARVIS' to get my attention.")

            while self.voice_mode_active:
                try:
                    # Listen for wake word or command
                    speech = await self.listen()

                    if not speech:
                        continue

                    # Check for wake word
                    if any(wake_word in speech.lower() for wake_word in ['hey jarvis', 'hi jarvis', 'ok jarvis']):
                        await self.speak("Yes? How can I help you?")

                        # Listen for actual command
                        command_speech = await self.listen()
                        if command_speech:
                            # Process command
                            command = await self.process_voice_command(command_speech)
                            if command:
                                await self.execute_voice_command(command)
                    else:
                        # Process speech directly as command
                        command = await self.process_voice_command(speech)
                        if command and command.intent != 'unknown':
                            await self.execute_voice_command(command)

                except Exception as e:
                    self.logger.error(f"❌ Voice interaction error: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"❌ Voice interaction loop failed: {e}")

    async def get_call_statistics(self) -> Dict[str, Any]:
        """Get calling system statistics"""
        try:
            total_calls = len(self.call_history)
            outgoing_calls = len([c for c in self.call_history if c.call_type == 'outgoing'])
            missed_calls = len([c for c in self.call_history if c.call_type == 'missed'])

            # Calculate average call duration
            completed_calls = [c for c in self.call_history if c.duration > 0]
            avg_duration = sum(c.duration for c in completed_calls) / len(completed_calls) if completed_calls else 0

            return {
                'total_contacts': len(self.contacts),
                'total_calls': total_calls,
                'outgoing_calls': outgoing_calls,
                'missed_calls': missed_calls,
                'average_call_duration': round(avg_duration, 1),
                'voice_enabled': self.voice_enabled,
                'voice_mode_active': self.voice_mode_active,
                'calling_enabled': self.calling_enabled,
                'call_in_progress': self.call_in_progress,
                'voice_commands_processed': len(self.voice_commands)
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get call statistics: {e}")
            return {}

    async def shutdown(self):
        """Shutdown voice and calling system"""
        try:
            # Disable voice mode
            await self.disable_voice_mode()

            # Save all data
            await self._save_contacts()
            await self._save_call_history()
            await self._save_voice_commands()

            self.logger.info("✅ Voice and Calling System v15 shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ Voice and Calling System shutdown failed: {e}")