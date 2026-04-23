import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { Bot, CheckCircle } from 'lucide-react';
import { telegram } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      bot_token: '',
      bot_username: '',
    },
  });
  
  const updateTokenMutation = useMutation({
    mutationFn: async (data: { bot_token: string; bot_username?: string }) => {
      await telegram.updateBotToken(data.bot_token, data.bot_username);
    },
    onSuccess: () => {
      setSuccess('Bot token updated successfully');
      setError('');
    },
    onError: () => {
      setError('Failed to update bot token');
      setSuccess('');
    },
  });
  
  const onSubmit = (data: any) => {
    updateTokenMutation.mutate(data);
  };
  
  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
      
      {/* Account Information */}
      <div className="card p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Information</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Username</p>
            <p className="text-base font-medium text-gray-900">{user?.username}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Email</p>
            <p className="text-base font-medium text-gray-900">{user?.email}</p>
          </div>
          {user?.business_name && (
            <div>
              <p className="text-sm text-gray-500">Business Name</p>
              <p className="text-base font-medium text-gray-900">{user.business_name}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Telegram Bot Configuration */}
      <div className="card p-6">
        <div className="flex items-center mb-4">
          <Bot className="w-6 h-6 text-primary-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Telegram Bot</h2>
        </div>
        
        {user?.telegram_bot_username && (
          <div className="flex items-center gap-2 mb-4 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm text-green-800">
              Connected to @{user.telegram_bot_username}
            </span>
          </div>
        )}
        
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-sm font-medium text-blue-900 mb-2">How to set up your Telegram bot:</h3>
          <ol className="text-sm text-blue-800 space-y-2 list-decimal list-inside">
            <li>Open Telegram and search for @BotFather</li>
            <li>Send /newbot and follow the instructions</li>
            <li>Copy the bot token provided by BotFather</li>
            <li>Paste the token below and save</li>
            <li>Your bot will automatically handle customer messages!</li>
          </ol>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {success && (
            <div className="p-4 bg-green-50 text-green-800 rounded-lg">
              {success}
            </div>
          )}
          
          {error && (
            <div className="p-4 bg-red-50 text-red-800 rounded-lg">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bot Token *
            </label>
            <input
              type="text"
              placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              className="input"
              {...register('bot_token', { required: 'Bot token is required' })}
            />
            {errors.bot_token && (
              <p className="mt-1 text-sm text-red-600">{errors.bot_token.message}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bot Username (Optional)
            </label>
            <input
              type="text"
              placeholder="your_bot_username"
              className="input"
              {...register('bot_username')}
            />
            <p className="mt-1 text-xs text-gray-500">
              Without the @ symbol
            </p>
          </div>
          
          <button
            type="submit"
            disabled={updateTokenMutation.isPending}
            className="btn btn-primary"
          >
            {updateTokenMutation.isPending ? 'Saving...' : 'Save Bot Configuration'}
          </button>
        </form>
      </div>
      
      {/* API Information */}
      <div className="card p-6 mt-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">API Information</h2>
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500">Webhook URL</p>
            <code className="block mt-1 p-3 bg-gray-50 rounded text-sm text-gray-900 overflow-x-auto">
              {import.meta.env.VITE_API_URL}/telegram/webhook
            </code>
          </div>
          <p className="text-sm text-gray-600">
            This webhook URL is automatically configured when you save your bot token.
            Telegram will send all customer messages to this endpoint.
          </p>
        </div>
      </div>
    </div>
  );
}
