import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents.agent_base import AgentBase  # 修改后的导入路径
from utils.logger import LOG  # 修改后的导入路径

import tempfile

class TestAgentBase(unittest.TestCase):

    def setUp(self):
        """
        在每个测试用例运行之前调用，用于初始化所需的资源。
        动态创建 mock_prompt.txt 和 mock_intro.json 文件。
        """
        # 创建临时文件夹，存放测试用的文件
        self.test_dir = tempfile.mkdtemp()

        # 创建 mock_prompt.txt 文件
        self.mock_prompt_file = os.path.join(self.test_dir, "mock_prompt.txt")
        with open(self.mock_prompt_file, "w", encoding="utf-8") as f:
            f.write("Test Prompt")

        # 创建 mock_intro.json 文件
        self.mock_intro_file = os.path.join(self.test_dir, "mock_intro.json")
        with open(self.mock_intro_file, "w", encoding="utf-8") as f:
            json.dump({"intro": "test"}, f)

        # 初始化 AgentBase 实例
        self.agent = AgentBase(name="TestAgent", prompt_file=self.mock_prompt_file, intro_file=self.mock_intro_file)

    @patch("builtins.open", mock_open(read_data="Test Prompt"))
    def test_load_prompt_valid(self):
        # 验证加载提示文件
        self.agent.prompt = "Test Prompt"
        self.assertEqual(self.agent.prompt, "Test Prompt")
    
    @patch("builtins.open", mock_open(read_data=json.dumps({"intro": "test"})))
    def test_load_intro_valid(self):
        # 验证加载介绍文件
        self.agent.intro_messages = {"intro": "test"}
        self.assertEqual(self.agent.intro_messages, {"intro": "test"})

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_prompt_file_not_found(self, mock_file):
        # 验证加载提示文件时找不到文件
        with self.assertRaises(FileNotFoundError):
            AgentBase(name="TestAgent", prompt_file="invalid_prompt.txt")
    
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_intro_file_not_found(self, mock_file):
        # 验证加载介绍文件时找不到文件
        with self.assertRaises(FileNotFoundError):
            AgentBase(name="TestAgent", prompt_file="mock_prompt.txt", intro_file="invalid_intro.json")

    @patch("builtins.open", side_effect=ValueError)
    def test_load_intro_json_decode_error(self, mock_file):
        # 验证加载介绍文件时JSON格式错误
        with self.assertRaises(ValueError):
            AgentBase(name="TestAgent", prompt_file="mock_prompt.txt", intro_file="invalid_intro.json")

    @patch("agents.agent_base.ChatOllama")  # 修改后的导入路径
    def test_create_chatbot(self, MockChatOllama):
        # 模拟 ChatOllama 的行为
        agent = self.agent
        # 验证创建聊天机器人
        self.assertIsNotNone(agent.chatbot)
        self.assertIsNotNone(agent.chatbot_with_history)

    @patch.object(AgentBase, "chat_with_history", return_value="Hello!")
    def test_chat_with_history(self, mock_invoke):
        # 模拟与聊天机器人交互
        agent = self.agent
        response = agent.chat_with_history("Hello")
        self.assertEqual(response, "Hello!")  # 验证输出
        mock_invoke.assert_called_once()  # 验证是否调用了 invoke 方法

    @patch("utils.logger.LOG.debug")
    def test_chat_with_history_logging(self, mock_log):
        # 创建一个模拟的 chatbot_with_history
        mock_response = MagicMock()
        mock_response.content = "Hello!"
        
        # 直接设置实例的 chatbot_with_history
        self.agent.chatbot_with_history = MagicMock()
        self.agent.chatbot_with_history.invoke.return_value = mock_response
        
        # 调用方法
        response = self.agent.chat_with_history("Hello")
        
        # 验证响应
        self.assertEqual(response, "Hello!")
        
        # 验证日志调用
        mock_log.assert_called_once_with("[ChatBot][TestAgent] Hello!")

    def tearDown(self):
        """
        在每个测试用例运行后调用，用于清理资源。
        删除在 setUp 中创建的临时文件和文件夹。
        """
        if os.path.exists(self.mock_prompt_file):
            os.remove(self.mock_prompt_file)
        if os.path.exists(self.mock_intro_file):
            os.remove(self.mock_intro_file)
        if os.path.isdir(self.test_dir):
            os.rmdir(self.test_dir)

if __name__ == '__main__':
    unittest.main()

