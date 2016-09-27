//
// Copyright (c) 2015-2016 Vinnie Falco (vinnie dot falco at gmail dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef EXAMPLE_HPP
#define EXAMPLE_HPP

#include <cstddef>
#include <string>

// This is a sample header file to show docca XLST results
//
// namespace, enum, type alias, global, static global,
// function, static function, struct/class

namespace example {

/** Enum

    Description
*/
enum enum_t
{
    /// 0
    zero,

    /// 1
    one,

    /// 2
    two
};

/** Enum class

    Description
*/
enum class enum_c
{
    /// aaa
    aaa,

    /// bbb
    bbb,

    /// ccc
    ccc
};

/** Type alias

    Description
*/
using type = std::string;

/** Template type alias

    Description
*/
template<class T>
using t_type = std::vector<T>;

/** Void or deduced

    Description
*/
using vod = void_or_deduced;

/** Implementation-defined

    Description
*/
using impdef = implementation_defined;

/** Variable

    Description
*/
extern std::size_t var;

/** Static variable

    Description
*/
static std::size_t s_var = 0;

/** Brief with @b bold text.

    Function returning @ref type.

    @return The type

    @see t_func.

    @throw std::exception on error
    @throw std::domain_error on bad parameters

    @par Thread Safety

    Cannot be called concurrently.

    @note Additional notes.

    @param arg1 Function parameter 1
    @param arg2 Function parameter 2
*/
type
func(int arg1, std::string arg2);

/** Brief.

    Function description.

    See @ref func.

    @tparam T Template parameter 1
    @tparam U Template parameter 2
    @tparam V Template parameter 3

    @param t Function parameter 1
    @param u Function parameter 2
    @param v Function parameter 3

    @return nothing
*/
template<class T, class U>
void
t_func(T t, U const& u, V&& v);

/** Overloaded function 1

    Description

    @param arg1 Parameter 1
*/
void
overload(int arg1);

/** Overloaded function 2

    Description

    @param arg1 Parameter 1
    @param arg2 Parameter 2
*/
void
overload(int arg1, int arg2);

/** Overloaded function 3

    Description

    @param arg1 Parameter 1
    @param arg2 Parameter 2
    @param arg3 Parameter 3
*/
void
overload(int arg1, int arg2, int arg3);

//------------------------------------------------------------------------------

namespace detail {

/** Detail class

    Description
*/
struct detail_type
{
};

/** Detail function

    Description
*/
void
detail_function();

} // detail

//------------------------------------------------------------------------------

/// Nested namespace
namespace nested {

/** Enum

    Description
*/
enum enum_t
{
    /// 0
    zero,

    /// 1
    one,

    /// 2
    two
};

/** Enum class

    Description
*/
enum class enum_c
{
    /// aaa
    aaa,

    /// bbb
    bbb,

    /// ccc
    ccc
};

/** Type alias

    Description
*/
using type = std::string;

/** Template type alias

    Description
*/
template<class T>
using t_type = std::vector<T>;

/** Variable

    Description
*/
extern std::size_t var;

/** Static variable

    Description
*/
static std::size_t s_var = 0;

/** Brief with @b bold text.

    Function returning @ref type.

    @return The type

    @see t_func.

    @throw std::exception on error
    @throw std::domain_error on bad parameters

    @par Thread Safety

    Cannot be called concurrently.

    @note Additional notes.

    @param arg1 Function parameter 1
    @param arg2 Function parameter 2
*/
type
func(int arg1, std::string arg2);

/** Brief.

    Function description.

    See @ref func.

    @tparam T Template parameter 1
    @tparam U Template parameter 2
    @tparam V Template parameter 3

    @param t Function parameter 1
    @param u Function parameter 2
    @param v Function parameter 3

    @return nothing
*/
template<class T, class U>
void
t_func(T t, U const& u, V&& v);

/** Overloaded function 1

    Description

    @param arg1 Parameter 1
*/
void
overload(int arg1);

/** Overloaded function 2

    Description

    @param arg1 Parameter 1
    @param arg2 Parameter 2
*/
void
overload(int arg1, int arg2);

/** Overloaded function 3

    Description

    @param arg1 Parameter 1
    @param arg2 Parameter 2
    @param arg3 Parameter 3
*/
void
overload(int arg1, int arg2, int arg3);

} // nested

/** Template class type.

    Description.

    @tparam T Template parameter 1
    @tparam U Template parameter 2
*/
template<class T, class U>
class class_type
{
public:
    /** Enum

        Description
    */
    enum enum_t
    {
        /// 0
        zero,

        /// 1
        one,

        /// 2
        two
    };

    /** Enum class

        Description
    */
    enum class enum_c
    {
        /// aaa
        aaa,

        /// bbb
        bbb,

        /// ccc
        ccc
    };

    /** Type alias

        Description
    */
    using type = std::string;

    /** Template type alias

        Description
    */
    template<class T>
    using t_type = std::vector<T>;

    /** Variable

        Description
    */
    extern std::size_t var;

    /** Static variable

        Description
    */
    static std::size_t s_var = 0;

    /** Brief with @b bold text.

        Function returning @ref type.

        @return The type

        @see t_func.

        @throw std::exception on error
        @throw std::domain_error on bad parameters

        @par Thread Safety

        Cannot be called concurrently.

        @note Additional notes.

        @param arg1 Function parameter 1
        @param arg2 Function parameter 2
    */
    type
    func(int arg1, std::string arg2);

    /** Brief.

        Function description.

        See @ref func.

        @tparam T Template parameter 1
        @tparam U Template parameter 2
        @tparam V Template parameter 3

        @param t Function parameter 1
        @param u Function parameter 2
        @param v Function parameter 3

        @return nothing
    */
    template<class T, class U>
    void
    t_func(T t, U const& u, V&& v);

    /** Overloaded function 1

        Description

        @param arg1 Parameter 1
    */
    void
    overload(int arg1);

    /** Overloaded function 2

        Description

        @param arg1 Parameter 1
        @param arg2 Parameter 2
    */
    void
    overload(int arg1, int arg2);

    /** Overloaded function 3

        Description

        @param arg1 Parameter 1
        @param arg2 Parameter 2
        @param arg3 Parameter 3
    */
    void
    overload(int arg1, int arg2, int arg3);

    /// Public data
    std::size_t pub_data_;

    /// Public static data
    static std::size_t pub_sdata_;

protected:
    /** Protected data

        Description
    */
    std::size_t prot_data_;

    /** Static protected data

        Description
    */
    static std::size_t prot_sdata_;

    /** Protected type

        Description
    */
    struct prot_type
    {
    };

    /** Protected function

        Description
    */
    void prot_memfn();

    /** Protected function returning @ref prot_type

        Description
    */
    prot_type prot_rvmemfn();

    /** Protected static member function

        Description
    */
    static void static_prot_memfn();

private:
    /** Private data

        Description
    */
    std::size_t priv_data_;

    /** Static private data

        Description
    */
    static std::size_t priv_sdata_;

    /** Private type

        Description
    */
    struct priv_type
    {
    };

    /** Private function

        Description
    */
    void priv_memfn();

    /** Private function returning *ref priv_type

        Description
    */
    priv_type priv_rvmemfn();

    /** Static private member function

        Description
    */
    static void static_priv_memfn();

    /** Friend class

        Description
    */
    friend friend_class;
};

/// Other base class 1
class other_base_class1
{
};

/// Other base class 2
class other_base_class2
{
};

/** Derived type

    Description
*/
template<class T, class U>
class derived_type :
    public class_type<T, U>,
    protected other_base_class1,
    private other_base_class2
{
};

/** References to all identifiers:

    Description one @ref one

    @par See Also

    @li @ref type

    @li @ref t_type

    @li @ref vod

    @li @ref impdef

    @li @ref var

    @li @ref s_var

    @li @ref func

    @li @ref t_func

    @li @ref overload

    @li @ref nested::enum_t : @ref nested::zero @ref nested::one @ref nested::two

    @li @ref nested::enum_c : nested::enum_c::aaa @ref nested::enum_c::bbb @ref nested::enum_c::ccc

    @li @ref nested::type

    @li @ref nested::t_type

    @li @ref nested::var

    @li @ref nested::s_var

    @li @ref nested::func

    @li @ref nested::t_func

    @li @ref nested::overload

    @li @ref class_type

    @li @ref class_type::enum_t : @ref class_type::zero @ref class_type::one @ref class_type::two

    @li @ref class_type::enum_c : class_type::enum_c::aaa @ref class_type::enum_c::bbb @ref class_type::enum_c::ccc

    @li @ref class_type::type

    @li @ref class_type::t_type

    @li @ref class_type::var

    @li @ref class_type::s_var

    @li @ref class_type::func

    @li @ref class_type::t_func

    @li @ref class_type::overload

    @li @ref class_type::pub_data_

    @li @ref class_type::pub_sdata_

    @li @ref class_type::prot_type

    @li @ref class_type::priv_type

    @li @ref derived_type
*/
void all_ref();

} // example

namespace other {

/// other function
void func();

/// other class
struct class_type
{
};

} // other

#endif
