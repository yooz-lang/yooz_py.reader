""" Python parser library for Yooz """

import re
import random
from typing import Optional


class YoozParser:
    """
    A parser for the Yooz, used for processing conversational patterns,
    replacements, rules, and more.
    
    to see more-detailed docstring for YoozParser: "YoozParser-docstring.txt"
    """
    
    def __init__(self):
        self.patterns = []
        self.definitions = {}
        self.stopWords = []
        self.keywords = []
        self.categories = []
        self.global_responses = []
        self.replacements = []
        self.rules = []
        self.additional_response = ""
        self.rules_value = 0.0
        self.memory = {}
        self.nested_messages = {}
        self.message_history = []
        self.last_message = ''
    
    def parse(self, input_text: str) -> None:
        """
        Parses the Yooz input to extract categories,
        patterns, replacements, etc...

        :param input_text: The input text containing Yooz syntax (str)
        :return: None
        """
        self._extract_categories(input_text)
        self._extract_general_definitions(input_text)
        self._extract_replacements(input_text)
        self._extract_conversational_patterns(input_text)
        self._extract_conditions(input_text)
        self._extract_stopwords(input_text)
        self._extract_additional_response(input_text)
        self._extract_rules_and_rules_number(input_text)
        self._extract_variables(input_text)
        self._extract_nested_messages(input_text)
    
    def get_response(self, user_message: str) -> str:
        """
        Generates a response based on the user's message
        by matching patterns and conditions.

        :param user_message: The user's message (str)
        :return: The generated response (str)
        """
        user_message = self._process_replacements(user_message)
        cleaned_message = self._remove_stop_words(user_message)
        final_response = ""
        visited_responses = set()
        
        self.last_message = user_message
        self.message_history.append(self.last_message)
        
        # generating bot-response for nested-messages
        if response := self._process_nested_messages(cleaned_message):
            return response  # else: bot-response will be generated in next steps
        
        # to process "keywords" base on "rules", if there is any keyword
        for pattern in self.patterns:
            if 'user_pattern' in pattern:
                if '{' in pattern['user_pattern'] and '}' in pattern['user_pattern']:
                    keywords = re.findall(r'\{(.*?)\}', pattern['user_pattern'])[0]
                    if '،' in keywords and '_' in keywords:
                        # raise SyntaxError: کلمات کلیدی باید یا با '،' یا با '_' جدا بشن و نه هر دو
                        pass
                    elif '،' in keywords:  # presence of all keywords in cleaned_message is necessary
                        final_response = self._process_keywords_split_by_comma(
                            keywords, cleaned_message, final_response, pattern
                        )
                    elif '_' in keywords:  # presence of one keyword in cleaned_message is sufficient
                        final_response = self._process_keywords_split_by_underscore(
                            keywords, cleaned_message, final_response, pattern
                        )
        
        while True:
            found_match = False
            for pattern in self.patterns:
                if "pattern" in pattern:  # if True: we have a conditional-pattern
                    if response := self._process_conditional_pattern(pattern, cleaned_message):
                        return response
                    break
                
                response = self._process_normal_pattern(pattern, cleaned_message)
                if response:
                    if response in visited_responses:
                        continue
                    visited_responses.add(response)
                    if response.endswith('!>'):
                        response = response[:-2].strip()
                        final_response += response + " "
                        found_match = True
                    else:
                        final_response += response
                        if self.additional_response:
                            final_response += " " + self.additional_response
                        
                        return final_response.strip()
            
            if not found_match:
                break

        if final_response:
            if self.additional_response:
                final_response += " " + self.additional_response
            return final_response.strip()
        else:
            response = "???? متاسفم، متوجه نشدم. ????"
            if self.additional_response:
                response += " " + self.additional_response
            return response
    
    # ---------------------------------------------------------------------
    # used in parse() :
    # (don't need docstring. the name of each methods shows its functionality!)
    
    def _extract_categories(self, input_text: str) -> None:
        category_regex = re.compile(r'(\S+)\s*\{(.*?)\}', re.DOTALL)
        for match in category_regex.finditer(input_text):
            category_name = match.group(1).strip()
            items = [item.strip() for item in match.group(2).split('،')]
            self.categories.append((category_name, items))
    
    def _extract_general_definitions(self, input_text: str) -> None:
        definition_regex = re.compile(
            r'#(\S+)\s*:\s*(.*?)\s*\.', flags=re.DOTALL
        )
        for match in definition_regex.finditer(input_text):
            key = match.group(1).strip()
            value = match.group(2).strip()
            self.definitions[key] = value
    
    def _extract_replacements(self, input_text: str) -> None:
        replacement_regex = re.compile(
            r'\{\s*(.*?)\s*\}\s*->\s*\{\s*(.*?)\s*\}'
        )
        for match in replacement_regex.finditer(input_text):
            source_words = [
                word.strip() for word in match.group(1).split('،')
            ]
            target_words = [
                word.strip() for word in match.group(2).split('،')
            ]
            self.replacements.extend(zip(source_words, target_words))
    
    def _extract_conversational_patterns(self, input_text: str) -> None:
        pattern_regex = re.compile(
            # r'\(\s*\+\s*(.*?)\s*-\s*(.*?)\s*\n(\s*\))?',
            r'\(\s*\+\s*(.*?)\s*-\s*(.*?)\)',
            flags=re.DOTALL
        )
        for match in pattern_regex.finditer(input_text):
            user_pattern = match.group(1).strip()
            bot_responses = [
                resp.strip() for resp in match.group(2).split('_')
            ]
            if not user_pattern:  # اگر الگوی کاربر خالی باشد
                self.global_responses.extend(bot_responses)
            else:
                self.patterns.append({
                    'user_pattern': user_pattern,
                    'bot_responses': bot_responses
                })
    
    def _extract_conditions(self, input_text: str) -> None:
        pattern_matches = re.findall(
            r'\(\s*\+\s*(.*?)\s*-\s*(.*?)\s*\)',
            string=input_text,
            flags=re.DOTALL
        )
        for match in pattern_matches:
            user_pattern = match[0].strip()
            bot_responses = [
                response.strip() for response in match[1].split('_')
            ]
            if not user_pattern:
                self.global_responses.extend(bot_responses)
            elif re.findall(
                    r'\[([^\]]+)\]', user_pattern, flags=re.DOTALL
            ):
                
                matches = re.findall(
                    r'\('
                    r'\s*\+\s*(.*?)\s*\.\s*'
                    r'\[(.*?)\]\s*:\s*'
                    r'\-\s*(.*?)\s*'
                    r'(?:!\[\s*(.*?)\s*\]\s*:\s*'
                    r'\-\s*(.*?)\s*)*'
                    r'!\s*:\s*'
                    r'\-\s*(.*?)\s*'
                    r'\)',
                    string=input_text
                )
                for match_ in matches:
                    self.patterns.append({
                        'pattern': match_[0].strip(),  # الگوی کاربر
                        'main_condition': match_[1].strip() if match_[1] else None,  # شرط اصلی
                        'main_response': match_[2].strip(),  # پاسخ اصلی
                        'optional_condition': match_[3].strip() if len(match_) > 3 and match_[3] else None,
                        # شرط اختیاری
                        'optional_response': match_[4].strip() if len(match_) > 4 and match_[4] else None,
                        # پاسخ اختیاری
                        'default_response': match_[5].strip()  # پاسخ پیش‌فرض
                    })
            else:
                pass
    
    def _extract_stopwords(self, input_text: str) -> None:
        stopwords_regex = re.compile(
            r'-\s*\{\s*(.*?)\s*\}', re.DOTALL
        )
        for match in stopwords_regex.finditer(input_text):
            words = [word.strip() for word in match.group(1).split('،')]
            self.stopWords.extend(words)
    
    def _extract_additional_response(self, input_text: str) -> None:
        additional_response_regex = re.compile(
            r'\+\s*\(\s*(.*?)\s*\)',
            flags=re.DOTALL
        )
        match = additional_response_regex.search(input_text)
        if match:
            self.additional_response = match.group(1).strip()
    
    def _extract_rules_and_rules_number(self, input_text: str) -> None:
        # Extract rules number
        rules_number_regex = re.compile(r'\[\[(\d+(\.\d+)?)\]\]')
        match = rules_number_regex.search(input_text)
        if match:
            self.rules_value = float(match.group(1))
        
        # Extract rules
        rules_regex = re.compile(
            r'\{\s*\[(\d+(\.\d+)?)\]\s*(.*?)\s*>\s*(.*?)\}'
        )
        for match in rules_regex.finditer(input_text):
            rule = float(match.group(1).strip())
            trigger = match.group(3).strip()
            response = match.group(4).strip()
            self.rules.append({
                'rule': rule,
                'trigger': trigger,
                'response': response
            })
    
    def _extract_variables(self, input_text: str) -> None:
        save_data_regex = re.compile(r'=\s*(\w+):\s*(\S+)')
        for match in save_data_regex.finditer(input_text):
            key = match.group(1).strip()
            value = match.group(2).strip()
            self.memory[key] = value
    
    def _extract_nested_messages(self, input_text: str) -> None:
        # Extract nested messages
        nested_message_regex = re.compile(
            r'\(\s*\+\s*([^\(\)]*?)\s*-\s*([^\(\)]*?)\s*(\(.*?\))\s*\)',
            flags=re.DOTALL
        )
        for match in nested_message_regex.finditer(input_text):
            parent_trigger = match.group(1).strip()
            parent_response = match.group(2).strip()
            nested_commands = match.group(3).strip()
            
            # Parse nested commands
            nested_patterns = []
            nested_regex = re.compile(
                r'\(\s*\+\s*(.*?)\s*-\s*(.*?)\s*\)',
                flags=re.DOTALL
            )
            for nested_match in nested_regex.finditer(nested_commands):
                nested_user_pattern = nested_match.group(1).strip()
                nested_bot_response = nested_match.group(2).strip()
                nested_patterns.append({
                    'user_pattern': nested_user_pattern,
                    'bot_responses': [nested_bot_response]
                })
            self.nested_messages[parent_trigger] = {
                'responses': parent_response.split("_"),
                'nested_patterns': nested_patterns
            }
    
    # ---------------------------------------------------------------------
    # used in get_response() :
    
    def _process_replacements(self, message: str) -> str:
        """
        Replaces keywords in the message using predefined replacements.
        
        :param message: The user's message (str)
        
        :return: The preprocessed message (str)
        """
        for source, target in self.replacements:
            message = re.sub(
                rf'\b{re.escape(source)}\b', target, message
            )
        return message
    
    def _remove_stop_words(self, message: str) -> str:
        """
        Removes 'stop words' from the user's message.
        
        :param message: The user's message (str)
        
        :return: The message without stop words (str)
        """
        words = message.split()
        filtered_words = [
            word for word in words if word not in self.stopWords
        ]
        return ' '.join(filtered_words)
    
    def _process_nested_messages(self, cleaned_message: str) -> Optional[str]:
        """
        generates bot-response if there is nested-messages
        
        :param cleaned_message:
            The message without stop words, provided by _remove_stop_words() (str)
        :return: The generated response (str)
        """
        for parent_trigger, nested_data in self.nested_messages.items():
            # to generate response for outer user-message (parent_trigger)
            regex = self._create_regex(parent_trigger)
            if regex.match(self.last_message):
                if regex.match(cleaned_message):
                    response = random.choice(nested_data['responses'])
                    self.last_message = cleaned_message
                    return response
            elif len(self.message_history) >= 2:  # To avoid errors when processing the first message
                if parent_trigger == self.message_history[-2]:
                    for nested_pattern in nested_data["nested_patterns"]:
                        # to generate response for inner (nested) user-message
                        regex = self._create_regex(nested_pattern['user_pattern'])
                        if regex.match(cleaned_message):
                            response = random.choice(nested_pattern['bot_responses'])
                            self.last_message = cleaned_message
                            return response
            return None
        
    def _process_keywords_split_by_comma(
        self, keywords, cleaned_message, final_response, pattern
    ) -> str:
        """
        ...
        presence of all keywords in cleaned_message is necessary
        """
        keyword_list = keywords.split('،')
        if all(keyword in cleaned_message for keyword in keyword_list):  # All keywords must exist
            final_response += random.choice(pattern['bot_responses']) + " "
            for rule in self.rules:
                if rule['trigger'] in final_response:
                    if self.rules_value <= rule['rule']:
                        trigger_index = final_response.find(rule['trigger']) + len(rule['trigger'])
                        final_response = final_response[:trigger_index] + " " + rule[
                            'response'] + final_response[trigger_index:]
        return final_response if final_response else ""
                        
    def _process_keywords_split_by_underscore(
        self, keywords, cleaned_message, final_response, pattern
    ) -> str:
        """
        ...
        presence of one keyword in cleaned_message  is sufficient
        """
        keyword_list = keywords.split('_')
        if any(keyword in cleaned_message for keyword in keyword_list):  # Any one keyword is sufficient
            final_response += random.choice(pattern['bot_responses']) + " "
            for rule in self.rules:
                if rule['trigger'] in final_response:
                    if self.rules_value <= rule['rule']:
                        trigger_index = final_response.find(rule['trigger']) + len(rule['trigger'])
                        final_response = final_response[:trigger_index] + " " + rule[
                            'response'] + final_response[trigger_index:]
                        print("====>>", final_response)
        return final_response if final_response else ""
    
    def _process_conditional_pattern(self, pattern, cleaned_message):
        """
        generates bot-response if there is conditional pattern (conditional conversation)
        
        :param pattern:
        :param cleaned_message:
        :return:
        """
        regex = self._create_regex(pattern['pattern'])
        match = regex.match(cleaned_message)
        if match:
            # Check conditions
            if self._evaluate_condition(pattern['main_condition'], match):
                return self._resolve_response(pattern['main_response'], match)
            elif (
                    pattern.get('optional_condition') and
                    self._evaluate_condition(pattern['optional_condition'], match)
            ):
                return self._resolve_response(pattern['optional_response'], match)
            else:
                return self._resolve_response(pattern['default_response'], match)
    
    def _process_normal_pattern(
        self,
        pattern: dict,
        cleaned_message: str,
    ) -> Optional[str]:
        """"""
        regex = self._create_regex(pattern['user_pattern'])
        match = regex.match(cleaned_message)
        if match:
            resp = random.choice(pattern['bot_responses'])
            resp = self._resolve_response(resp, match)
            for rule in self.rules:
                # بخش زیر در "#عراق" باگ ایجاد میکنه...!
                if rule['trigger'] in resp:
                    if self.rules_value <= rule['rule']:
                        trigger_index = resp.find(rule['trigger']) + len(rule['trigger'])
                        resp = resp[:trigger_index] + " " + rule['response'] + resp[trigger_index:]
            return resp
        return
    
    # ---------------------------------------------------------------------
    # others :
    
    def _create_regex(self, pattern: str) -> re.Pattern:
        """
        Converts a Yooz pattern to a regex-pattern for matching user messages.
        
        :param pattern: The Yooz pattern (str)
        
        :return: The compiled regex-pattern (re.Pattern)
        """
        for category, items in self.categories:
            pattern: str = pattern.replace(
                f'&{category}', f"({'|'.join(items)})"
            )
        regex_pattern = re.sub(r'\*([0-9]*)', r'(.*?)', pattern)
        return re.compile(f'^{regex_pattern}$')
    
    def _resolve_response(self, response: str, match: re.Match) -> str:
        """
        Resolves placeholders in the response template
        using match groups and stored variables.
        
        :param response: The response template (str)
        :param match: The regex-match object (re.Match)
        
        :return: The resolved response (str)
        """
        for i in range(1, len(match.groups()) + 1):
            response = response.replace(f'*{i}', match.group(i).strip())
        
        def replace_variable(match_: re.Match) -> str:
            """
            
            :param match_:
            
            :return:
            """
            key = match_.group(1)
            value = self.memory.get(key, None)
            if value:
                return value
            else:
                return f"{{missing:{key}}}"
        
        response = re.sub(r'=(\w+):\S+', replace_variable, response)
        response = re.sub(r'=(\w+)', replace_variable, response)
        
        # Replace definitions
        response = re.sub(
            r'#(\S+)',
            repl=lambda m: self.definitions.get(m.group(1), m.group(0)),
            string=response
        )
        return response
    
    def _evaluate_condition(self, condition: str, matches: re.Match):
        """
        evaluates conditional expressions in conditional patterns
        
        :param condition: extracted conditional expression
        :param matches:
        
        :return: the result of conditional expression
        """
        resolved_condition = self._resolve_response(condition, matches)
        return eval(resolved_condition)


if __name__ == "__main__":
    pass
