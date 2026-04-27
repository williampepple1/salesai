import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Bot, CheckCircle, CreditCard, User as UserIcon } from 'lucide-react';
import { UserProfile } from '@clerk/clerk-react';
import { telegram, auth } from '@/lib/api';

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const webhookUrl = import.meta.env.VITE_TELEGRAM_WEBHOOK_URL || `${import.meta.env.VITE_API_URL}/telegram/webhook`;
  
  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: auth.getCurrentUser,
  });

  const accountForm = useForm({
    values: {
      full_name: user?.full_name || '',
      business_name: user?.business_name || '',
      bank_name: user?.bank_name || '',
      account_name: user?.account_name || '',
      account_number: user?.account_number || '',
    },
  });
  
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

  const updateAccountMutation = useMutation({
    mutationFn: auth.updateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      setSuccess('Account and bank details saved successfully');
      setError('');
    },
    onError: () => {
      setError('Failed to save account details');
      setSuccess('');
    },
  });
  
  const onSubmit = (data: any) => {
    updateTokenMutation.mutate(data);
  };

  const onAccountSubmit = (data: any) => {
    updateAccountMutation.mutate(data);
  };
  
  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
      
      {/* Clerk User Profile */}
      <div className="card p-6 mb-6">
        <div className="flex items-center mb-4">
          <UserIcon className="w-6 h-6 text-primary-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Account & Security</h2>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Manage your account details, email, password, and security settings.
        </p>
        <UserProfile 
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "shadow-none border-0"
            }
          }}
        />
      </div>

      {/* Seller and Bank Details */}
      <div className="card p-6 mb-6">
        <div className="flex items-center mb-4">
          <CreditCard className="w-6 h-6 text-primary-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Seller & Payment Details</h2>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          These details are printed on invoice images sent to customers on Telegram.
        </p>

        <form onSubmit={accountForm.handleSubmit(onAccountSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Seller Name</label>
              <input className="input" {...accountForm.register('full_name')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
              <input className="input" {...accountForm.register('business_name')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Bank Name</label>
              <input className="input" placeholder="e.g. GTBank" {...accountForm.register('bank_name')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Account Name</label>
              <input className="input" placeholder="e.g. Sales AI Store" {...accountForm.register('account_name')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Account Number</label>
              <input className="input" placeholder="e.g. 0123456789" {...accountForm.register('account_number')} />
            </div>
          </div>

          <button
            type="submit"
            disabled={updateAccountMutation.isPending}
            className="btn btn-primary"
          >
            {updateAccountMutation.isPending ? 'Saving...' : 'Save Seller & Bank Details'}
          </button>
        </form>
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
              {webhookUrl}
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
