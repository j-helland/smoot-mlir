#pragma once

#include <stdexcept>

namespace units::backend {

class BackendError : public std::runtime_error {
public:
  using std::runtime_error::runtime_error;
};

} // namespace units::backend
