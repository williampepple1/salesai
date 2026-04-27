import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { orders as ordersApi } from '@/lib/api';
import { formatCurrency, formatDateTime } from '@/lib/utils';
import type { Order } from '@/types';

export default function OrdersPage() {
  const queryClient = useQueryClient();
  const [expandedOrder, setExpandedOrder] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  
  const { data: orders, isLoading } = useQuery({
    queryKey: ['orders', statusFilter],
    queryFn: () => ordersApi.getAll(statusFilter || undefined),
  });
  
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      ordersApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
  
  const handleStatusChange = async (orderId: number, newStatus: string) => {
    await updateStatusMutation.mutateAsync({ id: orderId, status: newStatus });
  };
  
  const toggleExpand = (orderId: number) => {
    setExpandedOrder(expandedOrder === orderId ? null : orderId);
  };
  
  const statuses = ['', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'];
  
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Orders</h1>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input w-48"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="shipped">Shipped</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading orders...</p>
        </div>
      ) : orders && orders.length > 0 ? (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Order #{order.id}
                      </h3>
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                        order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        order.status === 'confirmed' ? 'bg-blue-100 text-blue-800' :
                        order.status === 'shipped' ? 'bg-purple-100 text-purple-800' :
                        order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {order.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Customer</p>
                        <p className="font-medium text-gray-900">{order.customer_name}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Total</p>
                        <p className="font-medium text-gray-900">
                          {formatCurrency(order.total_amount, order.currency)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Date</p>
                        <p className="font-medium text-gray-900">
                          {formatDateTime(order.created_at)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Items</p>
                        <p className="font-medium text-gray-900">{order.items.length}</p>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => toggleExpand(order.id)}
                    className="ml-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    {expandedOrder === order.id ? (
                      <ChevronUp className="w-5 h-5" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </button>
                </div>
                
                {expandedOrder === order.id && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    {/* Order Items */}
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Order Items</h4>
                      <div className="space-y-2">
                        {order.items.map((item, index) => (
                          <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                            <div>
                              <p className="font-medium text-gray-900">{item.name}</p>
                              <p className="text-sm text-gray-500">Quantity: {item.quantity}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-gray-900">
                                {formatCurrency(item.total_price, order.currency)}
                              </p>
                              {item.discount_applied > 0 && (
                                <p className="text-sm text-green-600">
                                  -{formatCurrency(item.discount_applied, order.currency)} discount
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-500">Subtotal</span>
                          <span className="text-gray-900">{formatCurrency(order.subtotal, order.currency)}</span>
                        </div>
                        {order.discount_amount > 0 && (
                          <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-500">Discount</span>
                            <span className="text-green-600">
                              -{formatCurrency(order.discount_amount, order.currency)}
                            </span>
                          </div>
                        )}
                        <div className="flex justify-between text-base font-bold">
                          <span>Total</span>
                          <span>{formatCurrency(order.total_amount, order.currency)}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Customer Info */}
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Customer Information</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Name</p>
                          <p className="text-gray-900">{order.customer_name}</p>
                        </div>
                        {order.customer_phone && (
                          <div>
                            <p className="text-gray-500">Phone</p>
                            <p className="text-gray-900">{order.customer_phone}</p>
                          </div>
                        )}
                        {order.customer_address && (
                          <div className="col-span-2">
                            <p className="text-gray-500">Address</p>
                            <p className="text-gray-900">{order.customer_address}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Invoice and Payment Receipt */}
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Invoice & Payment</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Payment Status</p>
                          <p className="font-medium text-gray-900">
                            {order.payment_status || 'awaiting_payment'}
                          </p>
                        </div>
                        {order.invoice_url && (
                          <div>
                            <p className="text-gray-500">Invoice</p>
                            <a
                              href={order.invoice_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-primary-600 hover:underline"
                            >
                              View invoice image
                            </a>
                          </div>
                        )}
                        {order.receipt_url && (
                          <div>
                            <p className="text-gray-500">Customer Receipt</p>
                            <a
                              href={order.receipt_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-primary-600 hover:underline"
                            >
                              View receipt image
                            </a>
                          </div>
                        )}
                      </div>
                      {order.receipt_url && (
                        <img
                          src={order.receipt_url}
                          alt="Customer payment receipt"
                          className="mt-4 max-h-64 rounded-lg border border-gray-200"
                        />
                      )}
                    </div>
                    
                    {/* Update Status */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Update Status
                      </label>
                      <select
                        value={order.status}
                        onChange={(e) => handleStatusChange(order.id, e.target.value)}
                        className="input w-full md:w-64"
                      >
                        <option value="pending">Pending</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="shipped">Shipped</option>
                        <option value="delivered">Delivered</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
          <p className="text-gray-500">Orders will appear here once customers make purchases</p>
        </div>
      )}
    </div>
  );
}
