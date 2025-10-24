import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  MagnifyingGlassIcon,
  Squares2X2Icon,
  ListBulletIcon,
  ShoppingBagIcon,
  StarIcon,
  SparklesIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';
import { Product } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const ProductsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'price' | 'rating'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1000]);
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  // Fetch products
  const { data: productsResponse, isLoading, error } = useQuery({
    queryKey: ['products', currentPage],
    queryFn: () => apiService.getProducts({ 
      page: currentPage, 
      per_page: itemsPerPage 
    }),
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const totalProducts = productsResponse?.total || 0;
  const totalPages = Math.ceil(totalProducts / itemsPerPage);

  // Filter and sort products
  const filteredAndSortedProducts = useMemo(() => {
    const products = productsResponse?.items || [];
    let filtered = products.filter((product: Product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.description?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesPrice = product.price >= priceRange[0] && product.price <= priceRange[1];
      return matchesSearch && matchesPrice;
    });

    // Sort products
    filtered.sort((a: Product, b: Product) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'rating':
          comparison = (a.average_rating || 0) - (b.average_rating || 0);
          break;
        default:
          comparison = 0;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [productsResponse?.items, searchTerm, priceRange, sortBy, sortOrder]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <StarIcon
        key={i}
        className={`h-4 w-4 ${
          i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  const renderProductCard = (product: Product) => (
    <Link
      key={product.id}
      to={`/products/${product.id}`}
      className={`group ${viewMode === 'grid' ? 'card-hover' : 'card-hover flex items-center space-x-4 p-4'}`}
    >
      <div className={`${viewMode === 'grid' ? 'aspect-w-1 aspect-h-1 mb-4' : 'w-24 h-24'} overflow-hidden rounded-lg bg-gray-100`}>
        {product.images && product.images[0] ? (
          <img
            src={product.images[0]}
            alt={product.name}
            className={`${viewMode === 'grid' ? 'w-full h-48' : 'w-full h-full'} object-cover group-hover:scale-105 transition-transform duration-200`}
          />
        ) : product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className={`${viewMode === 'grid' ? 'w-full h-48' : 'w-full h-full'} object-cover group-hover:scale-105 transition-transform duration-200`}
          />
        ) : (
          <div className={`${viewMode === 'grid' ? 'w-full h-48' : 'w-full h-full'} bg-gray-200 flex items-center justify-center`}>
            <ShoppingBagIcon className="h-8 w-8 text-gray-400" />
          </div>
        )}
      </div>
      
      <div className={`${viewMode === 'grid' ? '' : 'flex-1'}`}>
        <h3 className={`font-semibold text-gray-100 mb-2 group-hover:text-primary-600 transition-colors ${viewMode === 'list' ? 'text-lg' : ''}`}>
          {product.name}
        </h3>
        
        {viewMode === 'list' && (
          <p className="text-gray-400 text-sm mb-2 line-clamp-2">
            {product.description}
          </p>
        )}
        
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl font-bold text-primary-600">
            ${product.price.toFixed(2)}
          </span>
          {product.average_rating && (
            <div className="flex items-center space-x-1">
              <div className="flex">
                {renderStars(product.average_rating)}
              </div>
              <span className="text-sm text-gray-500">
                ({product.review_count || 0})
              </span>
            </div>
          )}
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1 text-sm text-gray-500">
            <SparklesIcon className="h-4 w-4" />
            <span>AI Optimized</span>
          </div>
          <div className={`text-sm ${product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
          </div>
        </div>
      </div>
    </Link>
  );

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-screen bg-dark-900">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-100 mb-4">Products</h1>
        <p className="text-gray-400">
          Discover our AI-optimized product catalog with intelligent pricing and recommendations.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8">
        <div className="flex flex-col lg:flex-row gap-4 mb-4">
          {/* Search */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 text-gray-100 placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Sort */}
          <div className="flex items-center space-x-2">
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field as 'name' | 'price' | 'rating');
                setSortOrder(order as 'asc' | 'desc');
              }}
              className="px-3 py-2 border border-dark-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="name-asc">Name (A-Z)</option>
              <option value="name-desc">Name (Z-A)</option>
              <option value="price-asc">Price (Low-High)</option>
              <option value="price-desc">Price (High-Low)</option>
              <option value="rating-desc">Rating (High-Low)</option>
              <option value="rating-asc">Rating (Low-High)</option>
            </select>

            {/* View Mode Toggle */}
            <div className="flex border border-dark-600 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-primary-600 text-white' : 'bg-dark-800 text-gray-400 hover:bg-gray-50'}`}
              >
                <Squares2X2Icon className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-primary-600 text-white' : 'bg-dark-800 text-gray-400 hover:bg-gray-50'}`}
              >
                <ListBulletIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Filters Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-3 py-2 border border-dark-600 rounded-lg hover:bg-gray-50"
            >
              <AdjustmentsHorizontalIcon className="h-5 w-5" />
              <span>Filters</span>
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="bg-gray-50 p-4 rounded-lg border">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Price Range: ${priceRange[0]} - ${priceRange[1]}
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    min="0"
                    value={priceRange[0]}
                    onChange={(e) => setPriceRange([parseInt(e.target.value) || 0, priceRange[1]])}
                    className="w-20 px-2 py-1 border border-dark-600 rounded text-sm"
                    placeholder="Min"
                  />
                  <input
                    type="number"
                    min="0"
                    value={priceRange[1]}
                    onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value) || 1000])}
                    className="w-20 px-2 py-1 border border-dark-600 rounded text-sm"
                    placeholder="Max"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results Info */}
      <div className="mb-6 flex justify-between items-center">
        <p className="text-gray-400">
          {error ? (
            'Unable to load products. Please try again later.'
          ) : (
            `Showing ${filteredAndSortedProducts.length} of ${totalProducts} products`
          )}
        </p>
      </div>

      {/* Products Grid/List */}
      {error ? (
        <div className="text-center py-12">
          <ShoppingBagIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-100 mb-2">Unable to Load Products</h3>
          <p className="text-gray-400 mb-4">We're having trouble connecting to our product catalog.</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      ) : filteredAndSortedProducts.length === 0 ? (
        <div className="text-center py-12">
          <ShoppingBagIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-100 mb-2">No Products Found</h3>
          <p className="text-gray-400 mb-4">
            {searchTerm || priceRange[0] > 0 || priceRange[1] < 1000
              ? 'Try adjusting your search or filters.'
              : 'Our AI agents are working to stock our catalog with amazing products.'}
          </p>
          {(searchTerm || priceRange[0] > 0 || priceRange[1] < 1000) && (
            <button
              onClick={() => {
                setSearchTerm('');
                setPriceRange([0, 1000]);
              }}
              className="btn-outline"
            >
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
        }>
          {filteredAndSortedProducts.map(renderProductCard)}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && !error && (
        <div className="mt-12 flex justify-center">
          <div className="flex space-x-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-2 border border-dark-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
              return (
                <button
                  key={page}
                  onClick={() => handlePageChange(page)}
                  className={`px-3 py-2 border rounded-lg ${
                    currentPage === page
                      ? 'bg-primary-600 text-white border-primary-600'
                      : 'border-dark-600 hover:bg-gray-50'
                  }`}
                >
                  {page}
                </button>
              );
            })}
            
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-2 border border-dark-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsPage;