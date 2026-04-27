export interface User {
  id: number;
  clerk_user_id: string;
  email: string;
  username: string;
  full_name?: string;
  business_name?: string;
  bank_name?: string;
  account_name?: string;
  account_number?: string;
  telegram_bot_username?: string;
  is_active: boolean;
  created_at: string;
}

export interface Product {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  price: number;
  currency: string;
  image_urls: string[];
  stock_quantity: number;
  is_available: boolean;
  category?: string;
  created_at: string;
  updated_at?: string;
}

export interface DiscountRule {
  id: number;
  product_id: number;
  rule_name: string;
  discount_type: 'percentage' | 'fixed' | 'buy_x_get_y';
  quantity_threshold: number;
  discount_value: number;
  free_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface OrderItem {
  product_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  discount_applied: number;
  total_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  customer_name: string;
  customer_phone?: string;
  customer_address?: string;
  items: OrderItem[];
  subtotal: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  invoice_url?: string;
  receipt_url?: string;
  payment_status?: 'awaiting_payment' | 'receipt_submitted' | 'verified';
  notes?: string;
  created_at: string;
}

