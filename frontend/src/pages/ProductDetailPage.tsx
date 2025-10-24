import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ShoppingCartIcon,
  StarIcon,
  HeartIcon,
  ShareIcon,
  ChevronLeftIcon,
  SparklesIcon,
  ShoppingBagIcon,
  CheckIcon,
  XMarkIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { apiService } from '../services/api';
import { useCartStore } from '../stores/cartStore';
import { Product } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { addToCart, isLoading: cartLoading } = useCartStore();
  
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [isFavorited, setIsFavorited] = useState(false);

  // Fetch product details
  const { data: product, isLoading, error } = useQuery({
    queryKey: ['product', id],
    queryFn: () => apiService.getProduct(Number(id)),
    enabled: !!id,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch product recommendations
  const { data: recommendations } = useQuery({
    queryKey: ['product-recommendations', id],
    queryFn: () => apiService.getProductRecommendations(Number(id), 4),
    enabled: !!id,
    retry: 1,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  const handleAddToCart = async () => {
    if (!product) return;

    try {
      await addToCart(product.id, quantity);
      toast.success(`Added ${quantity} ${product.name}(s) to cart!`);
    } catch (error) {
      toast.error('Failed to add item to cart');
    }
  };

  const handleShare = async () => {
    if (navigator.share && product) {
      try {
        await navigator.share({
          title: product.name,
          text: product.description,
          url: window.location.href,
        });
      } catch (error) {
        // Fallback to copying URL
        navigator.clipboard.writeText(window.location.href);
        toast.success('Product link copied to clipboard!');
      }
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Product link copied to clipboard!');
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <StarIcon
        key={i}
        className={`h-5 w-5 ${
          i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <ShoppingBagIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Product Not Found</h1>
          <p className="text-gray-600 mb-8">
            The product you're looking for doesn't exist or has been removed.
          </p>
          <Link to="/products" className="btn-primary">
            Browse Products
          </Link>
        </div>
      </div>
    );
  }

  const images = product.images || (product.image_url ? [product.image_url] : []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="mb-8">
        <Link 
          to="/products" 
          className="inline-flex items-center text-primary-600 hover:text-primary-800"
        >
          <ChevronLeftIcon className="h-4 w-4 mr-1" />
          Back to Products
        </Link>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Product Images */}
        <div>
          <div className="aspect-w-1 aspect-h-1 mb-4 overflow-hidden rounded-lg bg-gray-100">
            {images.length > 0 ? (
              <img
                src={images[selectedImage]}
                alt={product.name}
                className="w-full h-96 object-cover"
              />
            ) : (
              <div className="w-full h-96 bg-gray-200 flex items-center justify-center">
                <ShoppingBagIcon className="h-24 w-24 text-gray-400" />
              </div>
            )}
          </div>
          
          {/* Image Thumbnails */}
          {images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {images.slice(0, 4).map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`aspect-w-1 aspect-h-1 overflow-hidden rounded border-2 ${
                    selectedImage === index ? 'border-primary-600' : 'border-gray-200'
                  }`}
                >
                  <img
                    src={image}
                    alt={`${product.name} ${index + 1}`}
                    className="w-full h-20 object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div>
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>
            
            {/* Rating */}
            {product.average_rating && (
              <div className="flex items-center space-x-2 mb-4">
                <div className="flex">
                  {renderStars(product.average_rating)}
                </div>
                <span className="text-sm text-gray-600">
                  {product.average_rating.toFixed(1)} ({product.review_count || 0} reviews)
                </span>
              </div>
            )}

            {/* Price */}
            <div className="flex items-center space-x-4 mb-6">
              <span className="text-4xl font-bold text-primary-600">
                ${product.price.toFixed(2)}
              </span>
              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <SparklesIcon className="h-4 w-4" />
                <span>AI Optimized Price</span>
              </div>
            </div>

            {/* Stock Status */}
            <div className="mb-6">
              {product.stock_quantity > 0 ? (
                <div className="flex items-center space-x-2 text-green-600">
                  <CheckIcon className="h-5 w-5" />
                  <span className="font-medium">
                    In Stock ({product.stock_quantity} available)
                  </span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-red-600">
                  <XMarkIcon className="h-5 w-5" />
                  <span className="font-medium">Out of Stock</span>
                </div>
              )}
            </div>
          </div>

          {/* Quantity and Add to Cart */}
          {product.stock_quantity > 0 && (
            <div className="mb-8">
              <div className="flex items-center space-x-4 mb-4">
                <label className="text-sm font-medium text-gray-700">Quantity:</label>
                <div className="flex items-center border border-gray-300 rounded">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-3 py-1 hover:bg-gray-50"
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <input
                    type="number"
                    min="1"
                    max={product.stock_quantity}
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, Math.min(product.stock_quantity, parseInt(e.target.value) || 1)))}
                    className="w-16 px-2 py-1 text-center border-0 focus:ring-0"
                  />
                  <button
                    onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                    className="px-3 py-1 hover:bg-gray-50"
                    disabled={quantity >= product.stock_quantity}
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleAddToCart}
                  disabled={cartLoading}
                  className="flex-1 btn-primary flex items-center justify-center"
                >
                  {cartLoading ? (
                    <LoadingSpinner size="sm" className="mr-2" />
                  ) : (
                    <ShoppingCartIcon className="h-5 w-5 mr-2" />
                  )}
                  Add to Cart
                </button>
                
                <button
                  onClick={() => setIsFavorited(!isFavorited)}
                  className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  {isFavorited ? (
                    <HeartIconSolid className="h-6 w-6 text-red-500" />
                  ) : (
                    <HeartIcon className="h-6 w-6 text-gray-400" />
                  )}
                </button>
                
                <button
                  onClick={handleShare}
                  className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <ShareIcon className="h-6 w-6 text-gray-400" />
                </button>
              </div>
            </div>
          )}

          {/* AI Features */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <div className="flex items-center space-x-2 mb-2">
              <CpuChipIcon className="h-5 w-5 text-blue-600" />
              <span className="font-medium text-blue-900">AI-Enhanced Product</span>
            </div>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Dynamically optimized pricing</li>
              <li>• Personalized for your preferences</li>
              <li>• Smart inventory management</li>
              <li>• Automated quality assurance</li>
            </ul>
          </div>

          {/* Description */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Description</h3>
            <div className="prose prose-sm text-gray-600">
              {product.description || 'No description available for this product.'}
            </div>
          </div>

          {/* Product Details */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Product Details</h3>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="font-medium text-gray-900">Product ID</dt>
                <dd className="text-gray-600">{product.id}</dd>
              </div>
              <div>
                <dt className="font-medium text-gray-900">Category</dt>
                <dd className="text-gray-600">{product.category?.name || 'Uncategorized'}</dd>
              </div>
              <div>
                <dt className="font-medium text-gray-900">Availability</dt>
                <dd className="text-gray-600">
                  {product.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}
                </dd>
              </div>
              <div>
                <dt className="font-medium text-gray-900">Status</dt>
                <dd className="text-gray-600">
                  {product.is_active ? 'Active' : 'Inactive'}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">You Might Also Like</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {recommendations.slice(0, 4).map((rec: Product) => (
              <Link
                key={rec.id}
                to={`/products/${rec.id}`}
                className="card-hover group"
              >
                <div className="aspect-w-1 aspect-h-1 mb-4 overflow-hidden rounded-lg bg-gray-100">
                  {rec.images && rec.images[0] ? (
                    <img
                      src={rec.images[0]}
                      alt={rec.name}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  ) : rec.image_url ? (
                    <img
                      src={rec.image_url}
                      alt={rec.name}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  ) : (
                    <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                      <ShoppingBagIcon className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                </div>
                
                <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                  {rec.name}
                </h3>
                
                <div className="flex items-center justify-between">
                  <span className="text-xl font-bold text-primary-600">
                    ${rec.price.toFixed(2)}
                  </span>
                  {rec.average_rating && (
                    <div className="flex items-center space-x-1">
                      <div className="flex">
                        {renderStars(rec.average_rating)}
                      </div>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetailPage;