//
// Copyright (c) 2020 Krystian Stasiowski (sdkrystian@gmail.com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef EXAMPLE_ISSUE_48_HPP
#define EXAMPLE_ISSUE_48_HPP

namespace example {
namespace detail {

class a_class
{
};

struct a_struct
{
};

} // detail

/** Issue 48

    Friends classes should not be listed unless
    docca is configured to show private members.
*/
class issue_48
{
    /// This should not be emitted.
    friend class detail::a_class;

    /// This should not be emitted.
    friend struct detail::a_struct;

public:
    void f();
};

} // example

#endif
