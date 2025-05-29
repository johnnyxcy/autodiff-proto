#define __MASMOD_VERSION__ "2025.05.28+rev.1"
#include "mas/libs/crobat/arrays/arrays.hpp"
#include "mas/libs/crobat/io/io.hpp"
#include "mas/libs/crobat/math/math.hpp"
#include "mas/libs/masmod/libc/headers.hpp"
#include <cmath>
#include <iostream>
#include <memory>
#include <string>

using mas::libs::crobat::arrays::loc;
using mas::libs::crobat::io::Err;
using mas::libs::crobat::io::Ok;
using mas::libs::crobat::io::Result;
using mas::libs::crobat::math::distribution::Rng;
using mas::libs::masmod::libc::mod::Advan;
using mas::libs::masmod::libc::mod::Cmt;
using mas::libs::masmod::libc::mod::IModule;
using mas::libs::masmod::libc::mod::Locals;
using mas::libs::masmod::libc::mod::ModuleType;
using mas::libs::masmod::libc::mod::NumericSharedVar;
using mas::libs::masmod::libc::mod::PredContext;
using mas::libs::masmod::libc::mod::PredVariant;
using mas::libs::masmod::libc::mod::SymbolTable;
using mas::libs::masmod::libc::mod::Trans;

// DECLARE_bool(PROTECTED);
namespace mas {
double log(double v) {
  // if (FLAGS_PROTECTED) {
  if (v <= 0) {
    return 0;
  } else {
    return std::log(v);
  }
  //}
  return std::log(v);
}

} // namespace mas

enum __SymbolTableVarName { __SymbolTableVarName___self_DV };
static std::unordered_map<std::string, __SymbolTableVarName>
    __symtab_varname_mp = {{"__self_DV", __SymbolTableVarName___self_DV}};
class __SymbolTable : public SymbolTable {
public:
  double __self_pop_cl = 0.0;
  double __self_pop_v = 0.0;
  double __self_pop_ka = 0.0;
  double __self_iiv_cl = 0.0;
  double __self_iiv_v = 0.0;
  double __self_iiv_ka = 0.0;
  double __self_eps_add = 0.0;
  Cmt *__self_cmt1 = nullptr;
  Cmt *__self_cmt2 = nullptr;
  double __self_DV = 0.0;
  void put_theta(const unsigned int &varname, const double &entity) override {
    switch (varname) {
    case 0:
      this->__self_pop_cl = entity;
      break;
    case 1:
      this->__self_pop_v = entity;
      break;
    case 2:
      this->__self_pop_ka = entity;
      break;
    default:
      break;
    }
  }
  void put_eta(const unsigned int &varname, const double &entity) override {
    switch (varname) {
    case 0:
      this->__self_iiv_cl = entity;
      break;
    case 1:
      this->__self_iiv_v = entity;
      break;
    case 2:
      this->__self_iiv_ka = entity;
      break;
    default:
      break;
    }
  }
  void put_eps(const unsigned int &varname, const double &entity) override {
    switch (varname) {
    case 0:
      this->__self_eps_add = entity;
      break;
    default:
      break;
    }
  }
  void put_numeric(const std::string &varname, const double &entity) override {
    switch (__symtab_varname_mp[varname]) {
    case __SymbolTableVarName___self_DV:
      this->__self_DV = entity;
      break;
    default:
      break;
    }
  }
  void put_string(const std::string &varname,
                  const std::string &entity) override {
    switch (__symtab_varname_mp[varname]) {
    default:
      break;
    }
  }
  void put_cmt(const unsigned int &varname, Cmt *entity) override {
    switch (varname) {
    case 0:
      this->__self_cmt1 = entity;
      break;
    case 1:
      this->__self_cmt2 = entity;
      break;
    default:
      break;
    }
  }
};

class __Module : public IModule {
public:
  ModuleType module_type() const { return ModuleType::MODULE_TYPE_ODE; }
  std::unique_ptr<SymbolTable> create_symbol_table() const {
    return std::make_unique<__SymbolTable>();
  }
  Advan advan_type() const { return Advan::ADVAN_UNKNOWN; }
  Trans trans_type() const { return Trans::TRANS_UNKNOWN; }
  Result<void> __pred(PredContext *__ctx) {
    // #region Declarations
    __SymbolTable *__msymtab = reinterpret_cast<__SymbolTable *>(__ctx->symtab);
    Locals *__locals = __ctx->locals;
    double __self_pop_cl = __msymtab->__self_pop_cl;
    double __self_pop_v = __msymtab->__self_pop_v;
    double __self_pop_ka = __msymtab->__self_pop_ka;
    double __self_iiv_cl = __msymtab->__self_iiv_cl;
    double __self_iiv_v = __msymtab->__self_iiv_v;
    double __self_iiv_ka = __msymtab->__self_iiv_ka;
    double __self_eps_add = __msymtab->__self_eps_add;
    double cl = 0.;
    double __X_0 = 0.;
    double __X_1 = 0.;
    double __X_2 = 0.;
    double __X_3 = 0.;
    double __X_4 = 0.;
    double __X_5 = 0.;
    double v = 0.;
    double __X_6 = 0.;
    double __X_7 = 0.;
    double __X_8 = 0.;
    double __X_9 = 0.;
    double __X_10 = 0.;
    double __X_11 = 0.;
    double ka = 0.;
    double __X_12 = 0.;
    double __X_13 = 0.;
    double __X_14 = 0.;
    double __X_15 = 0.;
    double __X_16 = 0.;
    double __X_17 = 0.;
    double k = 0.;
    double __0 = 0.;
    double __1 = 0.;
    double __2 = 0.;
    double __3 = 0.;
    double __X_18 = 0.;
    double __X_19 = 0.;
    double __X_20 = 0.;
    double __X_21 = 0.;
    double __X_22 = 0.;
    double __X_23 = 0.;
    double IPRED = 0.;
    double __X_24 = 0.;
    double __X_25 = 0.;
    double __X_26 = 0.;
    double __X_27 = 0.;
    double __X_28 = 0.;
    double __X_29 = 0.;
    double __add__a = 0.;
    double __X_30 = 0.;
    double __X_31 = 0.;
    double __X_32 = 0.;
    double __X_33 = 0.;
    double __X_34 = 0.;
    double __X_35 = 0.;
    double __add__b = 0.;
    double __X_36 = 0.;
    double __X_37 = 0.;
    double __X_38 = 0.;
    double __X_39 = 0.;
    double __X_40 = 0.;
    double __X_41 = 0.;
    double __add__return = 0.;
    double __X_42 = 0.;
    double __X_43 = 0.;
    double __X_44 = 0.;
    double __X_45 = 0.;
    double __X_46 = 0.;
    double __X_47 = 0.;
    double RES = 0.;
    double __X_48 = 0.;
    double __X_49 = 0.;
    double __X_50 = 0.;
    double __X_51 = 0.;
    double __X_52 = 0.;
    double __X_53 = 0.;
    double __normal_cdf__x = 0.;
    double __X_54 = 0.;
    double __X_55 = 0.;
    double __X_56 = 0.;
    double __X_57 = 0.;
    double __X_58 = 0.;
    double __X_59 = 0.;
    double __normal_cdf__A1 = 0.;
    double __normal_cdf__A2 = 0.;
    double __normal_cdf__A3 = 0.;
    double __normal_cdf__A4 = 0.;
    double __normal_cdf__A5 = 0.;
    double __normal_cdf__RSQRT2PI = 0.;
    double __normal_cdf__abs_x = 0.;
    double __X_60 = 0.;
    double __X_61 = 0.;
    double __X_62 = 0.;
    double __X_63 = 0.;
    double __X_64 = 0.;
    double __X_65 = 0.;
    double __normal_cdf__K = 0.;
    double __X_66 = 0.;
    double __X_67 = 0.;
    double __X_68 = 0.;
    double __X_69 = 0.;
    double __X_70 = 0.;
    double __X_71 = 0.;
    double __normal_cdf__K4 = 0.;
    double __X_72 = 0.;
    double __X_73 = 0.;
    double __X_74 = 0.;
    double __X_75 = 0.;
    double __X_76 = 0.;
    double __X_77 = 0.;
    double __normal_cdf__K3 = 0.;
    double __X_78 = 0.;
    double __X_79 = 0.;
    double __X_80 = 0.;
    double __X_81 = 0.;
    double __X_82 = 0.;
    double __X_83 = 0.;
    double __normal_cdf__K2 = 0.;
    double __X_84 = 0.;
    double __X_85 = 0.;
    double __X_86 = 0.;
    double __X_87 = 0.;
    double __X_88 = 0.;
    double __X_89 = 0.;
    double __normal_cdf__K1 = 0.;
    double __X_90 = 0.;
    double __X_91 = 0.;
    double __X_92 = 0.;
    double __X_93 = 0.;
    double __X_94 = 0.;
    double __X_95 = 0.;
    double __normal_cdf__cnd = 0.;
    double __4 = 0.;
    double __5 = 0.;
    double __6 = 0.;
    double __7 = 0.;
    double __8 = 0.;
    double __9 = 0.;
    double __10 = 0.;
    double __11 = 0.;
    double __12 = 0.;
    double __13 = 0.;
    double __X_96 = 0.;
    double __X_97 = 0.;
    double __X_98 = 0.;
    double __X_99 = 0.;
    double __X_100 = 0.;
    double __X_101 = 0.;
    double __normal_cdf__return = 0.;
    double __X_102 = 0.;
    double __X_103 = 0.;
    double __X_104 = 0.;
    double __X_105 = 0.;
    double __X_106 = 0.;
    double __X_107 = 0.;
    double CUM = 0.;
    double __X_108 = 0.;
    double __X_109 = 0.;
    double __X_110 = 0.;
    double __X_111 = 0.;
    double __X_112 = 0.;
    double __X_113 = 0.;
    // #endregion

    // #region Body

    // cl = self.pop_cl * exp(self.iiv_cl)
    cl = __self_pop_cl * std::exp(__self_iiv_cl);
    if (__ctx->first_order) {

      // __X__["cl", self.iiv_cl] = self.pop_cl * exp(self.iiv_cl)
      __X_0 = __self_pop_cl * std::exp(__self_iiv_cl);

      // __X__["cl", self.iiv_v] = 0
      __X_1 = 0;

      // __X__["cl", self.iiv_ka] = 0
      __X_2 = 0;

      // __X__["cl", self.eps_add] = 0
      __X_3 = 0;

      // __X__["cl", __A__[self.cmt1]] = 0
      __X_4 = 0;

      // __X__["cl", __A__[self.cmt2]] = 0
      __X_5 = 0;
    }

    // v = self.pop_v * exp(self.iiv_v)
    v = __self_pop_v * std::exp(__self_iiv_v);
    if (__ctx->first_order) {

      // __X__["v", self.iiv_cl] = 0
      __X_6 = 0;

      // __X__["v", self.iiv_v] = self.pop_v * exp(self.iiv_v)
      __X_7 = __self_pop_v * std::exp(__self_iiv_v);

      // __X__["v", self.iiv_ka] = 0
      __X_8 = 0;

      // __X__["v", self.eps_add] = 0
      __X_9 = 0;

      // __X__["v", __A__[self.cmt1]] = 0
      __X_10 = 0;

      // __X__["v", __A__[self.cmt2]] = 0
      __X_11 = 0;
    }

    // ka = self.pop_ka * exp(self.iiv_ka)
    ka = __self_pop_ka * std::exp(__self_iiv_ka);
    if (__ctx->first_order) {

      // __X__["ka", self.iiv_cl] = 0
      __X_12 = 0;

      // __X__["ka", self.iiv_v] = 0
      __X_13 = 0;

      // __X__["ka", self.iiv_ka] = self.pop_ka * exp(self.iiv_ka)
      __X_14 = __self_pop_ka * std::exp(__self_iiv_ka);

      // __X__["ka", self.eps_add] = 0
      __X_15 = 0;

      // __X__["ka", __A__[self.cmt1]] = 0
      __X_16 = 0;

      // __X__["ka", __A__[self.cmt2]] = 0
      __X_17 = 0;
    }

    // k = cl / v
    k = cl * std::pow(v, -1);
    if (__ctx->first_order) {

      // __0 = v ** -1
      __0 = std::pow(v, -1);

      // __1 = cl * v ** -2
      __1 = cl * std::pow(v, -2);

      // __2 = __1 * __X__["v", __A__[self.cmt1]]
      __2 = __1 * __X_10;

      // __3 = __1 * __X__["v", __A__[self.cmt2]]
      __3 = __1 * __X_11;

      // __X__["k", self.iiv_cl] = __A__[self.cmt1, self.iiv_cl] * __0 *
      // __X__["cl", __A__[self.cmt1]] + -1 * __A__[self.cmt1, self.iiv_cl] *
      // __2 + __A__[self.cmt2, self.iiv_cl] * __0 * __X__["cl",
      // __A__[self.cmt2]] + -1 * __A__[self.cmt2, self.iiv_cl] * __3 + __0 *
      // __X__["cl", self.iiv_cl] + -1 * __1 * __X__["v", self.iiv_cl]
      __X_18 = __0 * __X_0 + -1 * __1 * __X_6 + -1 * __2 * __ctx->ode->A[2] +
               -1 * __3 * __ctx->ode->A[3] + __0 * __ctx->ode->A[2] * __X_4 +
               __0 * __ctx->ode->A[3] * __X_5;

      // __X__["k", self.iiv_v] = __A__[self.cmt1, self.iiv_v] * __0 *
      // __X__["cl", __A__[self.cmt1]] + -1 * __A__[self.cmt1, self.iiv_v] * __2
      // + __A__[self.cmt2, self.iiv_v] * __0 * __X__["cl", __A__[self.cmt2]] +
      // -1 * __A__[self.cmt2, self.iiv_v] * __3 + __0 * __X__["cl", self.iiv_v]
      // + -1 * __1 * __X__["v", self.iiv_v]
      __X_19 = __0 * __X_1 + -1 * __1 * __X_7 + -1 * __2 * __ctx->ode->A[4] +
               -1 * __3 * __ctx->ode->A[5] + __0 * __ctx->ode->A[4] * __X_4 +
               __0 * __ctx->ode->A[5] * __X_5;

      // __X__["k", self.iiv_ka] = __A__[self.cmt1, self.iiv_ka] * __0 *
      // __X__["cl", __A__[self.cmt1]] + -1 * __A__[self.cmt1, self.iiv_ka] *
      // __2 + __A__[self.cmt2, self.iiv_ka] * __0 * __X__["cl",
      // __A__[self.cmt2]] + -1 * __A__[self.cmt2, self.iiv_ka] * __3 + __0 *
      // __X__["cl", self.iiv_ka] + -1 * __1 * __X__["v", self.iiv_ka]
      __X_20 = __0 * __X_2 + -1 * __1 * __X_8 + -1 * __2 * __ctx->ode->A[6] +
               -1 * __3 * __ctx->ode->A[7] + __0 * __ctx->ode->A[6] * __X_4 +
               __0 * __ctx->ode->A[7] * __X_5;

      // __X__["k", self.eps_add] = __A__[self.cmt1, self.eps_add] * __0 *
      // __X__["cl", __A__[self.cmt1]] + -1 * __A__[self.cmt1, self.eps_add] *
      // __2 + __A__[self.cmt2, self.eps_add] * __0 * __X__["cl",
      // __A__[self.cmt2]] + -1 * __A__[self.cmt2, self.eps_add] * __3 + __0 *
      // __X__["cl", self.eps_add] + -1 * __1 * __X__["v", self.eps_add]
      __X_21 = __0 * __X_3 + -1 * __1 * __X_9 + -1 * __2 * 0. + -1 * __3 * 0. +
               __0 * 0. * __X_4 + __0 * 0. * __X_5;

      // __X__["k", __A__[self.cmt1]] = __0 * __X__["cl", __A__[self.cmt1]] + -1
      // * __2
      __X_22 = -1 * __2 + __0 * __X_4;

      // __X__["k", __A__[self.cmt2]] = __0 * __X__["cl", __A__[self.cmt2]] + -1
      // * __3
      __X_23 = -1 * __3 + __0 * __X_5;
    }

    // __DADT__[self.cmt1] = -ka * self.cmt1.A
    __ctx->ode->dAdt[0] = -1 * ka * __ctx->ode->A[0];
    if (__ctx->first_order) {

      // __0 = __A__[self.cmt1] * __X__["ka", __A__[self.cmt1]]
      __0 = __ctx->ode->A[0] * __X_16;

      // __1 = __A__[self.cmt1] * __X__["ka", __A__[self.cmt2]]
      __1 = __ctx->ode->A[0] * __X_17;

      // __DADT__[self.cmt1, self.iiv_cl] = -1 * __A__[self.cmt1] * __X__["ka",
      // self.iiv_cl] + -1 * __A__[self.cmt1, self.iiv_cl] * __0 + -1 *
      // __A__[self.cmt1, self.iiv_cl] * ka + -1 * __A__[self.cmt2, self.iiv_cl]
      // * __1
      __ctx->ode->dAdt[2] =
          -1 * __0 * __ctx->ode->A[2] + -1 * __1 * __ctx->ode->A[3] +
          -1 * ka * __ctx->ode->A[2] + -1 * __ctx->ode->A[0] * __X_12;

      // __DADT__[self.cmt1, self.iiv_v] = -1 * __A__[self.cmt1] * __X__["ka",
      // self.iiv_v] + -1 * __A__[self.cmt1, self.iiv_v] * __0 + -1 *
      // __A__[self.cmt1, self.iiv_v] * ka + -1 * __A__[self.cmt2, self.iiv_v] *
      // __1
      __ctx->ode->dAdt[4] =
          -1 * __0 * __ctx->ode->A[4] + -1 * __1 * __ctx->ode->A[5] +
          -1 * ka * __ctx->ode->A[4] + -1 * __ctx->ode->A[0] * __X_13;

      // __DADT__[self.cmt1, self.iiv_ka] = -1 * __A__[self.cmt1] * __X__["ka",
      // self.iiv_ka] + -1 * __A__[self.cmt1, self.iiv_ka] * __0 + -1 *
      // __A__[self.cmt1, self.iiv_ka] * ka + -1 * __A__[self.cmt2, self.iiv_ka]
      // * __1
      __ctx->ode->dAdt[6] =
          -1 * __0 * __ctx->ode->A[6] + -1 * __1 * __ctx->ode->A[7] +
          -1 * ka * __ctx->ode->A[6] + -1 * __ctx->ode->A[0] * __X_14;

      // __DADT__[self.cmt1, self.eps_add] = -1 * __A__[self.cmt1] * __X__["ka",
      // self.eps_add] + -1 * __A__[self.cmt1, self.eps_add] * __0 + -1 *
      // __A__[self.cmt1, self.eps_add] * ka + -1 * __A__[self.cmt2,
      // self.eps_add] * __1

      // __DADT__[self.cmt1, __A__[self.cmt1]] = -1 * __0 + -1 * ka
      __ctx->ode->dA[0] = -1 * __0 + -1 * ka;

      // __DADT__[self.cmt1, __A__[self.cmt2]] = -1 * __1
      __ctx->ode->dA[1] = -1 * __1;
    }

    // __DADT__[self.cmt2] = ka * self.cmt1.A - k * self.cmt2.A
    __ctx->ode->dAdt[1] = ka * __ctx->ode->A[0] + -1 * k * __ctx->ode->A[1];
    if (__ctx->first_order) {

      // __0 = __A__[self.cmt1] * __X__["ka", __A__[self.cmt1]]
      __0 = __ctx->ode->A[0] * __X_16;

      // __1 = __A__[self.cmt1] * __X__["ka", __A__[self.cmt2]]
      __1 = __ctx->ode->A[0] * __X_17;

      // __2 = __A__[self.cmt2] * __X__["k", __A__[self.cmt1]]
      __2 = __ctx->ode->A[1] * __X_22;

      // __3 = __A__[self.cmt2] * __X__["k", __A__[self.cmt2]]
      __3 = __ctx->ode->A[1] * __X_23;

      // __DADT__[self.cmt2, self.iiv_cl] = __A__[self.cmt1] * __X__["ka",
      // self.iiv_cl] + -1 * __A__[self.cmt2] * __X__["k", self.iiv_cl] +
      // __A__[self.cmt1, self.iiv_cl] * __0 + -1 * __A__[self.cmt1,
      // self.iiv_cl] * __2 + __A__[self.cmt1, self.iiv_cl] * ka +
      // __A__[self.cmt2, self.iiv_cl] * __1 + -1 * __A__[self.cmt2,
      // self.iiv_cl] * __3 + -1 * __A__[self.cmt2, self.iiv_cl] * k
      __ctx->ode->dAdt[3] =
          __0 * __ctx->ode->A[2] + __1 * __ctx->ode->A[3] +
          ka * __ctx->ode->A[2] + __ctx->ode->A[0] * __X_12 +
          -1 * __2 * __ctx->ode->A[2] + -1 * __3 * __ctx->ode->A[3] +
          -1 * k * __ctx->ode->A[3] + -1 * __ctx->ode->A[1] * __X_18;

      // __DADT__[self.cmt2, self.iiv_v] = __A__[self.cmt1] * __X__["ka",
      // self.iiv_v] + -1 * __A__[self.cmt2] * __X__["k", self.iiv_v] +
      // __A__[self.cmt1, self.iiv_v] * __0 + -1 * __A__[self.cmt1, self.iiv_v]
      // * __2 + __A__[self.cmt1, self.iiv_v] * ka + __A__[self.cmt2,
      // self.iiv_v] * __1 + -1 * __A__[self.cmt2, self.iiv_v] * __3 + -1 *
      // __A__[self.cmt2, self.iiv_v] * k
      __ctx->ode->dAdt[5] =
          __0 * __ctx->ode->A[4] + __1 * __ctx->ode->A[5] +
          ka * __ctx->ode->A[4] + __ctx->ode->A[0] * __X_13 +
          -1 * __2 * __ctx->ode->A[4] + -1 * __3 * __ctx->ode->A[5] +
          -1 * k * __ctx->ode->A[5] + -1 * __ctx->ode->A[1] * __X_19;

      // __DADT__[self.cmt2, self.iiv_ka] = __A__[self.cmt1] * __X__["ka",
      // self.iiv_ka] + -1 * __A__[self.cmt2] * __X__["k", self.iiv_ka] +
      // __A__[self.cmt1, self.iiv_ka] * __0 + -1 * __A__[self.cmt1,
      // self.iiv_ka] * __2 + __A__[self.cmt1, self.iiv_ka] * ka +
      // __A__[self.cmt2, self.iiv_ka] * __1 + -1 * __A__[self.cmt2,
      // self.iiv_ka] * __3 + -1 * __A__[self.cmt2, self.iiv_ka] * k
      __ctx->ode->dAdt[7] =
          __0 * __ctx->ode->A[6] + __1 * __ctx->ode->A[7] +
          ka * __ctx->ode->A[6] + __ctx->ode->A[0] * __X_14 +
          -1 * __2 * __ctx->ode->A[6] + -1 * __3 * __ctx->ode->A[7] +
          -1 * k * __ctx->ode->A[7] + -1 * __ctx->ode->A[1] * __X_20;

      // __DADT__[self.cmt2, self.eps_add] = __A__[self.cmt1] * __X__["ka",
      // self.eps_add] + -1 * __A__[self.cmt2] * __X__["k", self.eps_add] +
      // __A__[self.cmt1, self.eps_add] * __0 + -1 * __A__[self.cmt1,
      // self.eps_add] * __2 + __A__[self.cmt1, self.eps_add] * ka +
      // __A__[self.cmt2, self.eps_add] * __1 + -1 * __A__[self.cmt2,
      // self.eps_add] * __3 + -1 * __A__[self.cmt2, self.eps_add] * k

      // __DADT__[self.cmt2, __A__[self.cmt1]] = __0 + -1 * __2 + ka
      __ctx->ode->dA[2] = __0 + ka + -1 * __2;

      // __DADT__[self.cmt2, __A__[self.cmt2]] = __A__[self.cmt1] * __X__["ka",
      // __A__[self.cmt2]] + -1 * __3 + -1 * k
      __ctx->ode->dA[3] = -1 * __3 + -1 * k + __ctx->ode->A[0] * __X_17;
    }

    // __CMTP__[self.cmt1, "ALAG"] = -1 * k
    __self_cmt1->ALAG(0, 0) = -1 * k;
    if (__ctx->first_order) {

      // __CMTP__[self.cmt1, "ALAG", self.iiv_cl] = -1 * __A__[self.cmt1,
      // self.iiv_cl] * __X__["k", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.iiv_cl] * __X__["k", __A__[self.cmt2]] + -1 * __X__["k",
      // self.iiv_cl]
      __self_cmt1->ALAG(1, 0) = -1 * __X_18 + -1 * __ctx->ode->A[2] * __X_22 +
                                -1 * __ctx->ode->A[3] * __X_23;

      // __CMTP__[self.cmt1, "ALAG", self.iiv_v] = -1 * __A__[self.cmt1,
      // self.iiv_v] * __X__["k", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.iiv_v] * __X__["k", __A__[self.cmt2]] + -1 * __X__["k",
      // self.iiv_v]
      __self_cmt1->ALAG(2, 0) = -1 * __X_19 + -1 * __ctx->ode->A[4] * __X_22 +
                                -1 * __ctx->ode->A[5] * __X_23;

      // __CMTP__[self.cmt1, "ALAG", self.iiv_ka] = -1 * __A__[self.cmt1,
      // self.iiv_ka] * __X__["k", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.iiv_ka] * __X__["k", __A__[self.cmt2]] + -1 * __X__["k",
      // self.iiv_ka]
      __self_cmt1->ALAG(3, 0) = -1 * __X_20 + -1 * __ctx->ode->A[6] * __X_22 +
                                -1 * __ctx->ode->A[7] * __X_23;

      // __CMTP__[self.cmt1, "ALAG", self.eps_add] = -1 * __A__[self.cmt1,
      // self.eps_add] * __X__["k", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.eps_add] * __X__["k", __A__[self.cmt2]] + -1 * __X__["k",
      // self.eps_add]

      // __CMTP__[self.cmt1, "ALAG", __A__[self.cmt1]] = -1 * __X__["k",
      // __A__[self.cmt1]]

      // __CMTP__[self.cmt1, "ALAG", __A__[self.cmt2]] = -1 * __X__["k",
      // __A__[self.cmt2]]
    }

    // __CMTP__[self.cmt2, "A0"] = -1 * ka
    __self_cmt2->A0(0, 0) = -1 * ka;
    if (__ctx->first_order) {

      // __CMTP__[self.cmt2, "A0", self.iiv_cl] = -1 * __A__[self.cmt1,
      // self.iiv_cl] * __X__["ka", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.iiv_cl] * __X__["ka", __A__[self.cmt2]] + -1 * __X__["ka",
      // self.iiv_cl]
      __self_cmt2->A0(1, 0) = -1 * __X_12 + -1 * __ctx->ode->A[2] * __X_16 +
                              -1 * __ctx->ode->A[3] * __X_17;

      // __CMTP__[self.cmt2, "A0", self.iiv_v] = -1 * __A__[self.cmt1,
      // self.iiv_v] * __X__["ka", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.iiv_v] * __X__["ka", __A__[self.cmt2]] + -1 * __X__["ka",
      // self.iiv_v]
      __self_cmt2->A0(2, 0) = -1 * __X_13 + -1 * __ctx->ode->A[4] * __X_16 +
                              -1 * __ctx->ode->A[5] * __X_17;

      // __CMTP__[self.cmt2, "A0", self.iiv_ka] = -1 * __A__[self.cmt1,
      // self.iiv_ka] * __X__["ka", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.iiv_ka] * __X__["ka", __A__[self.cmt2]] + -1 * __X__["ka",
      // self.iiv_ka]
      __self_cmt2->A0(3, 0) = -1 * __X_14 + -1 * __ctx->ode->A[6] * __X_16 +
                              -1 * __ctx->ode->A[7] * __X_17;

      // __CMTP__[self.cmt2, "A0", self.eps_add] = -1 * __A__[self.cmt1,
      // self.eps_add] * __X__["ka", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
      // self.eps_add] * __X__["ka", __A__[self.cmt2]] + -1 * __X__["ka",
      // self.eps_add]

      // __CMTP__[self.cmt2, "A0", __A__[self.cmt1]] = -1 * __X__["ka",
      // __A__[self.cmt1]]

      // __CMTP__[self.cmt2, "A0", __A__[self.cmt2]] = -1 * __X__["ka",
      // __A__[self.cmt2]]
    }

    // IPRED = self.cmt2.A / v
    IPRED = std::pow(v, -1) * __ctx->ode->A[1];
    if (__ctx->first_order) {

      // __0 = v ** -1
      __0 = std::pow(v, -1);

      // __1 = __A__[self.cmt2] * v ** -2
      __1 = std::pow(v, -2) * __ctx->ode->A[1];

      // __2 = __1 * __X__["v", __A__[self.cmt1]]
      __2 = __1 * __X_10;

      // __3 = __1 * __X__["v", __A__[self.cmt2]]
      __3 = __1 * __X_11;

      // __X__["IPRED", self.iiv_cl] = -1 * __A__[self.cmt1, self.iiv_cl] * __2
      // + __A__[self.cmt2, self.iiv_cl] * __0 + -1 * __A__[self.cmt2,
      // self.iiv_cl] * __3 + -1 * __1 * __X__["v", self.iiv_cl]
      __X_24 = __0 * __ctx->ode->A[3] + -1 * __1 * __X_6 +
               -1 * __2 * __ctx->ode->A[2] + -1 * __3 * __ctx->ode->A[3];

      // __X__["IPRED", self.iiv_v] = -1 * __A__[self.cmt1, self.iiv_v] * __2 +
      // __A__[self.cmt2, self.iiv_v] * __0 + -1 * __A__[self.cmt2, self.iiv_v]
      // * __3 + -1 * __1 * __X__["v", self.iiv_v]
      __X_25 = __0 * __ctx->ode->A[5] + -1 * __1 * __X_7 +
               -1 * __2 * __ctx->ode->A[4] + -1 * __3 * __ctx->ode->A[5];

      // __X__["IPRED", self.iiv_ka] = -1 * __A__[self.cmt1, self.iiv_ka] * __2
      // + __A__[self.cmt2, self.iiv_ka] * __0 + -1 * __A__[self.cmt2,
      // self.iiv_ka] * __3 + -1 * __1 * __X__["v", self.iiv_ka]
      __X_26 = __0 * __ctx->ode->A[7] + -1 * __1 * __X_8 +
               -1 * __2 * __ctx->ode->A[6] + -1 * __3 * __ctx->ode->A[7];

      // __X__["IPRED", self.eps_add] = -1 * __A__[self.cmt1, self.eps_add] *
      // __2 + __A__[self.cmt2, self.eps_add] * __0 + -1 * __A__[self.cmt2,
      // self.eps_add] * __3 + -1 * __1 * __X__["v", self.eps_add]
      __X_27 = __0 * 0. + -1 * __1 * __X_9 + -1 * __2 * 0. + -1 * __3 * 0.;

      // __X__["IPRED", __A__[self.cmt1]] = -1 * __2
      __X_28 = -1 * __2;

      // __X__["IPRED", __A__[self.cmt2]] = __0 + -1 * __3
      __X_29 = __0 + -1 * __3;
    }
    if (IPRED <= 0) {

      // __add__a = self.DV
      __add__a = DV;
      if (__ctx->first_order) {

        // __X__["__add__a", self.iiv_cl] = 0
        __X_30 = 0;

        // __X__["__add__a", self.iiv_v] = 0
        __X_31 = 0;

        // __X__["__add__a", self.iiv_ka] = 0
        __X_32 = 0;

        // __X__["__add__a", self.eps_add] = 0
        __X_33 = 0;

        // __X__["__add__a", __A__[self.cmt1]] = 0
        __X_34 = 0;

        // __X__["__add__a", __A__[self.cmt2]] = 0
        __X_35 = 0;
      }

      // __add__b = -IPRED
      __add__b = -1 * IPRED;
      if (__ctx->first_order) {

        // __X__["__add__b", self.iiv_cl] = -1 * __A__[self.cmt1, self.iiv_cl] *
        // __X__["IPRED", __A__[self.cmt1]] + -1 * __A__[self.cmt2, self.iiv_cl]
        // * __X__["IPRED", __A__[self.cmt2]] + -1 * __X__["IPRED", self.iiv_cl]
        __X_36 = -1 * __X_24 + -1 * __ctx->ode->A[2] * __X_28 +
                 -1 * __ctx->ode->A[3] * __X_29;

        // __X__["__add__b", self.iiv_v] = -1 * __A__[self.cmt1, self.iiv_v] *
        // __X__["IPRED", __A__[self.cmt1]] + -1 * __A__[self.cmt2, self.iiv_v]
        // * __X__["IPRED", __A__[self.cmt2]] + -1 * __X__["IPRED", self.iiv_v]
        __X_37 = -1 * __X_25 + -1 * __ctx->ode->A[4] * __X_28 +
                 -1 * __ctx->ode->A[5] * __X_29;

        // __X__["__add__b", self.iiv_ka] = -1 * __A__[self.cmt1, self.iiv_ka] *
        // __X__["IPRED", __A__[self.cmt1]] + -1 * __A__[self.cmt2, self.iiv_ka]
        // * __X__["IPRED", __A__[self.cmt2]] + -1 * __X__["IPRED", self.iiv_ka]
        __X_38 = -1 * __X_26 + -1 * __ctx->ode->A[6] * __X_28 +
                 -1 * __ctx->ode->A[7] * __X_29;

        // __X__["__add__b", self.eps_add] = -1 * __A__[self.cmt1, self.eps_add]
        // * __X__["IPRED", __A__[self.cmt1]] + -1 * __A__[self.cmt2,
        // self.eps_add] * __X__["IPRED", __A__[self.cmt2]] + -1 *
        // __X__["IPRED", self.eps_add]
        __X_39 = -1 * __X_27 + -1 * 0. * __X_28 + -1 * 0. * __X_29;

        // __X__["__add__b", __A__[self.cmt1]] = -1 * __X__["IPRED",
        // __A__[self.cmt1]]
        __X_40 = -1 * __X_28;

        // __X__["__add__b", __A__[self.cmt2]] = -1 * __X__["IPRED",
        // __A__[self.cmt2]]
        __X_41 = -1 * __X_29;
      }

      // __add__return = __add__a + __add__b
      __add__return = __add__a + __add__b;
      if (__ctx->first_order) {

        // __X__["__add__return", self.iiv_cl] = __A__[self.cmt1, self.iiv_cl] *
        // __X__["__add__a", __A__[self.cmt1]] + __A__[self.cmt1, self.iiv_cl] *
        // __X__["__add__b", __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] *
        // __X__["__add__a", __A__[self.cmt2]] + __A__[self.cmt2, self.iiv_cl] *
        // __X__["__add__b", __A__[self.cmt2]] + __X__["__add__a", self.iiv_cl]
        // + __X__["__add__b", self.iiv_cl]
        __X_42 = __ctx->ode->A[2] * __X_34 + __ctx->ode->A[2] * __X_40 +
                 __ctx->ode->A[3] * __X_35 + __ctx->ode->A[3] * __X_41 +
                 __X_30 + __X_36;

        // __X__["__add__return", self.iiv_v] = __A__[self.cmt1, self.iiv_v] *
        // __X__["__add__a", __A__[self.cmt1]] + __A__[self.cmt1, self.iiv_v] *
        // __X__["__add__b", __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_v] *
        // __X__["__add__a", __A__[self.cmt2]] + __A__[self.cmt2, self.iiv_v] *
        // __X__["__add__b", __A__[self.cmt2]] + __X__["__add__a", self.iiv_v] +
        // __X__["__add__b", self.iiv_v]
        __X_43 = __ctx->ode->A[4] * __X_34 + __ctx->ode->A[4] * __X_40 +
                 __ctx->ode->A[5] * __X_35 + __ctx->ode->A[5] * __X_41 +
                 __X_31 + __X_37;

        // __X__["__add__return", self.iiv_ka] = __A__[self.cmt1, self.iiv_ka] *
        // __X__["__add__a", __A__[self.cmt1]] + __A__[self.cmt1, self.iiv_ka] *
        // __X__["__add__b", __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] *
        // __X__["__add__a", __A__[self.cmt2]] + __A__[self.cmt2, self.iiv_ka] *
        // __X__["__add__b", __A__[self.cmt2]] + __X__["__add__a", self.iiv_ka]
        // + __X__["__add__b", self.iiv_ka]
        __X_44 = __ctx->ode->A[6] * __X_34 + __ctx->ode->A[6] * __X_40 +
                 __ctx->ode->A[7] * __X_35 + __ctx->ode->A[7] * __X_41 +
                 __X_32 + __X_38;

        // __X__["__add__return", self.eps_add] = __A__[self.cmt1, self.eps_add]
        // * __X__["__add__a", __A__[self.cmt1]] + __A__[self.cmt1,
        // self.eps_add] * __X__["__add__b", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.eps_add] * __X__["__add__a", __A__[self.cmt2]]
        // + __A__[self.cmt2, self.eps_add] * __X__["__add__b",
        // __A__[self.cmt2]] + __X__["__add__a", self.eps_add] +
        // __X__["__add__b", self.eps_add]
        __X_45 = 0. * __X_34 + 0. * __X_40 + 0. * __X_35 + 0. * __X_41 +
                 __X_33 + __X_39;

        // __X__["__add__return", __A__[self.cmt1]] = __X__["__add__a",
        // __A__[self.cmt1]] + __X__["__add__b", __A__[self.cmt1]]
        __X_46 = __X_34 + __X_40;

        // __X__["__add__return", __A__[self.cmt2]] = __X__["__add__a",
        // __A__[self.cmt2]] + __X__["__add__b", __A__[self.cmt2]]
        __X_47 = __X_35 + __X_41;
      }

      // RES = __add__return
      RES = __add__return;
      if (__ctx->first_order) {

        // __X__["RES", self.iiv_cl] = __A__[self.cmt1, self.iiv_cl] *
        // __X__["__add__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.iiv_cl] * __X__["__add__return", __A__[self.cmt2]] +
        // __X__["__add__return", self.iiv_cl]
        __X_48 = __ctx->ode->A[2] * __X_46 + __ctx->ode->A[3] * __X_47 + __X_42;

        // __X__["RES", self.iiv_v] = __A__[self.cmt1, self.iiv_v] *
        // __X__["__add__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.iiv_v] * __X__["__add__return", __A__[self.cmt2]] +
        // __X__["__add__return", self.iiv_v]
        __X_49 = __ctx->ode->A[4] * __X_46 + __ctx->ode->A[5] * __X_47 + __X_43;

        // __X__["RES", self.iiv_ka] = __A__[self.cmt1, self.iiv_ka] *
        // __X__["__add__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.iiv_ka] * __X__["__add__return", __A__[self.cmt2]] +
        // __X__["__add__return", self.iiv_ka]
        __X_50 = __ctx->ode->A[6] * __X_46 + __ctx->ode->A[7] * __X_47 + __X_44;

        // __X__["RES", self.eps_add] = __A__[self.cmt1, self.eps_add] *
        // __X__["__add__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.eps_add] * __X__["__add__return", __A__[self.cmt2]] +
        // __X__["__add__return", self.eps_add]
        __X_51 = 0. * __X_46 + 0. * __X_47 + __X_45;

        // __X__["RES", __A__[self.cmt1]] = __X__["__add__return",
        // __A__[self.cmt1]]
        __X_52 = __X_46;

        // __X__["RES", __A__[self.cmt2]] = __X__["__add__return",
        // __A__[self.cmt2]]
        __X_53 = __X_47;
      }

      // __normal_cdf__x = RES
      __normal_cdf__x = RES;
      if (__ctx->first_order) {

        // __X__["__normal_cdf__x", self.iiv_cl] = __A__[self.cmt1, self.iiv_cl]
        // * __X__["RES", __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] *
        // __X__["RES", __A__[self.cmt2]] + __X__["RES", self.iiv_cl]
        __X_54 = __ctx->ode->A[2] * __X_52 + __ctx->ode->A[3] * __X_53 + __X_48;

        // __X__["__normal_cdf__x", self.iiv_v] = __A__[self.cmt1, self.iiv_v] *
        // __X__["RES", __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_v] *
        // __X__["RES", __A__[self.cmt2]] + __X__["RES", self.iiv_v]
        __X_55 = __ctx->ode->A[4] * __X_52 + __ctx->ode->A[5] * __X_53 + __X_49;

        // __X__["__normal_cdf__x", self.iiv_ka] = __A__[self.cmt1, self.iiv_ka]
        // * __X__["RES", __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] *
        // __X__["RES", __A__[self.cmt2]] + __X__["RES", self.iiv_ka]
        __X_56 = __ctx->ode->A[6] * __X_52 + __ctx->ode->A[7] * __X_53 + __X_50;

        // __X__["__normal_cdf__x", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __X__["RES", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.eps_add] * __X__["RES", __A__[self.cmt2]] + __X__["RES",
        // self.eps_add]
        __X_57 = 0. * __X_52 + 0. * __X_53 + __X_51;

        // __X__["__normal_cdf__x", __A__[self.cmt1]] = __X__["RES",
        // __A__[self.cmt1]]
        __X_58 = __X_52;

        // __X__["__normal_cdf__x", __A__[self.cmt2]] = __X__["RES",
        // __A__[self.cmt2]]
        __X_59 = __X_53;
      }

      // __normal_cdf__A1 = 0.31938153
      __normal_cdf__A1 = 0.31938153;

      // __normal_cdf__A2 = -0.356563782
      __normal_cdf__A2 = -0.356563782;

      // __normal_cdf__A3 = 1.781477937
      __normal_cdf__A3 = 1.781477937;

      // __normal_cdf__A4 = -1.821255978
      __normal_cdf__A4 = -1.821255978;

      // __normal_cdf__A5 = 1.330274429
      __normal_cdf__A5 = 1.330274429;

      // __normal_cdf__RSQRT2PI = 0.39894228040143267793994605993438
      __normal_cdf__RSQRT2PI = 0.3989422804014327;

      // __normal_cdf__abs_x = __normal_cdf__x
      __normal_cdf__abs_x = __normal_cdf__x;
      if (__ctx->first_order) {

        // __X__["__normal_cdf__abs_x", self.iiv_cl] = __A__[self.cmt1,
        // self.iiv_cl] * __X__["__normal_cdf__x", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_cl] * __X__["__normal_cdf__x",
        // __A__[self.cmt2]] + __X__["__normal_cdf__x", self.iiv_cl]
        __X_60 = __ctx->ode->A[2] * __X_58 + __ctx->ode->A[3] * __X_59 + __X_54;

        // __X__["__normal_cdf__abs_x", self.iiv_v] = __A__[self.cmt1,
        // self.iiv_v] * __X__["__normal_cdf__x", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__x",
        // __A__[self.cmt2]] + __X__["__normal_cdf__x", self.iiv_v]
        __X_61 = __ctx->ode->A[4] * __X_58 + __ctx->ode->A[5] * __X_59 + __X_55;

        // __X__["__normal_cdf__abs_x", self.iiv_ka] = __A__[self.cmt1,
        // self.iiv_ka] * __X__["__normal_cdf__x", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_ka] * __X__["__normal_cdf__x",
        // __A__[self.cmt2]] + __X__["__normal_cdf__x", self.iiv_ka]
        __X_62 = __ctx->ode->A[6] * __X_58 + __ctx->ode->A[7] * __X_59 + __X_56;

        // __X__["__normal_cdf__abs_x", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __X__["__normal_cdf__x", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.eps_add] * __X__["__normal_cdf__x",
        // __A__[self.cmt2]] + __X__["__normal_cdf__x", self.eps_add]
        __X_63 = 0. * __X_58 + 0. * __X_59 + __X_57;

        // __X__["__normal_cdf__abs_x", __A__[self.cmt1]] =
        // __X__["__normal_cdf__x", __A__[self.cmt1]]
        __X_64 = __X_58;

        // __X__["__normal_cdf__abs_x", __A__[self.cmt2]] =
        // __X__["__normal_cdf__x", __A__[self.cmt2]]
        __X_65 = __X_59;
      }
      if (__normal_cdf__x <= 0) {

        // __normal_cdf__abs_x = -__normal_cdf__x
        __normal_cdf__abs_x = -1 * __normal_cdf__x;
        if (__ctx->first_order) {

          // __X__["__normal_cdf__abs_x", self.iiv_cl] = -1 * __A__[self.cmt1,
          // self.iiv_cl] * __X__["__normal_cdf__x", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.iiv_cl] * __X__["__normal_cdf__x",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__x", self.iiv_cl]
          __X_60 = -1 * __X_54 + -1 * __ctx->ode->A[2] * __X_58 +
                   -1 * __ctx->ode->A[3] * __X_59;

          // __X__["__normal_cdf__abs_x", self.iiv_v] = -1 * __A__[self.cmt1,
          // self.iiv_v] * __X__["__normal_cdf__x", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__x",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__x", self.iiv_v]
          __X_61 = -1 * __X_55 + -1 * __ctx->ode->A[4] * __X_58 +
                   -1 * __ctx->ode->A[5] * __X_59;

          // __X__["__normal_cdf__abs_x", self.iiv_ka] = -1 * __A__[self.cmt1,
          // self.iiv_ka] * __X__["__normal_cdf__x", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.iiv_ka] * __X__["__normal_cdf__x",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__x", self.iiv_ka]
          __X_62 = -1 * __X_56 + -1 * __ctx->ode->A[6] * __X_58 +
                   -1 * __ctx->ode->A[7] * __X_59;

          // __X__["__normal_cdf__abs_x", self.eps_add] = -1 * __A__[self.cmt1,
          // self.eps_add] * __X__["__normal_cdf__x", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.eps_add] * __X__["__normal_cdf__x",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__x", self.eps_add]
          __X_63 = -1 * __X_57 + -1 * 0. * __X_58 + -1 * 0. * __X_59;

          // __X__["__normal_cdf__abs_x", __A__[self.cmt1]] = -1 *
          // __X__["__normal_cdf__x", __A__[self.cmt1]]
          __X_64 = -1 * __X_58;

          // __X__["__normal_cdf__abs_x", __A__[self.cmt2]] = -1 *
          // __X__["__normal_cdf__x", __A__[self.cmt2]]
          __X_65 = -1 * __X_59;
        }
      }

      // __normal_cdf__K = 1.0 / (1.0 + 0.2316419 * __normal_cdf__abs_x)
      __normal_cdf__K =
          1.00000000000000 *
          std::pow(1.00000000000000 + 0.231641900000000 * __normal_cdf__abs_x,
                   -1);
      if (__ctx->first_order) {

        // __0 = 0.231641900000000 * 0.231641900000000 * __normal_cdf__abs_x
        // + 1.00000000000000 ** -2
        __0 = 1.00000000000000 + 0.0536579698356100 * __normal_cdf__abs_x;

        // __1 = __0 * __X__["__normal_cdf__abs_x", __A__[self.cmt1]]
        __1 = __0 * __X_64;

        // __2 = __0 * __X__["__normal_cdf__abs_x", __A__[self.cmt2]]
        __2 = __0 * __X_65;

        // __X__["__normal_cdf__K", self.iiv_cl] = -1 * __A__[self.cmt1,
        // self.iiv_cl] * __1 + -1 * __A__[self.cmt2, self.iiv_cl] * __2 + -1 *
        // __0 * __X__["__normal_cdf__abs_x", self.iiv_cl]
        __X_66 = -1 * __0 * __X_60 + -1 * __1 * __ctx->ode->A[2] +
                 -1 * __2 * __ctx->ode->A[3];

        // __X__["__normal_cdf__K", self.iiv_v] = -1 * __A__[self.cmt1,
        // self.iiv_v] * __1 + -1 * __A__[self.cmt2, self.iiv_v] * __2 + -1 *
        // __0 * __X__["__normal_cdf__abs_x", self.iiv_v]
        __X_67 = -1 * __0 * __X_61 + -1 * __1 * __ctx->ode->A[4] +
                 -1 * __2 * __ctx->ode->A[5];

        // __X__["__normal_cdf__K", self.iiv_ka] = -1 * __A__[self.cmt1,
        // self.iiv_ka] * __1 + -1 * __A__[self.cmt2, self.iiv_ka] * __2 + -1 *
        // __0 * __X__["__normal_cdf__abs_x", self.iiv_ka]
        __X_68 = -1 * __0 * __X_62 + -1 * __1 * __ctx->ode->A[6] +
                 -1 * __2 * __ctx->ode->A[7];

        // __X__["__normal_cdf__K", self.eps_add] = -1 * __A__[self.cmt1,
        // self.eps_add] * __1 + -1 * __A__[self.cmt2, self.eps_add] * __2 + -1
        // * __0 * __X__["__normal_cdf__abs_x", self.eps_add]
        __X_69 = -1 * __0 * __X_63 + -1 * __1 * 0. + -1 * __2 * 0.;

        // __X__["__normal_cdf__K", __A__[self.cmt1]] = -1 * __1
        __X_70 = -1 * __1;

        // __X__["__normal_cdf__K", __A__[self.cmt2]] = -1 * __2
        __X_71 = -1 * __2;
      }

      // __normal_cdf__K4 = __normal_cdf__A4 + __normal_cdf__K *
      // __normal_cdf__A5
      __normal_cdf__K4 = __normal_cdf__A4 + __normal_cdf__A5 * __normal_cdf__K;
      if (__ctx->first_order) {

        // __0 = __normal_cdf__A5 * __X__["__normal_cdf__K", __A__[self.cmt1]]
        __0 = __normal_cdf__A5 * __X_70;

        // __1 = __normal_cdf__K * __X__["__normal_cdf__A5", __A__[self.cmt1]]
        __1 = __normal_cdf__K * 0.0;

        // __2 = __normal_cdf__A5 * __X__["__normal_cdf__K", __A__[self.cmt2]]
        __2 = __normal_cdf__A5 * __X_71;

        // __3 = __normal_cdf__K * __X__["__normal_cdf__A5", __A__[self.cmt2]]
        __3 = __normal_cdf__K * 0.0;

        // __X__["__normal_cdf__K4", self.iiv_cl] = __A__[self.cmt1,
        // self.iiv_cl] * __0 + __A__[self.cmt1, self.iiv_cl] * __1 +
        // __A__[self.cmt1, self.iiv_cl] * __X__["__normal_cdf__A4",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] * __2 +
        // __A__[self.cmt2, self.iiv_cl] * __3 + __A__[self.cmt2, self.iiv_cl] *
        // __X__["__normal_cdf__A4", __A__[self.cmt2]] + __normal_cdf__A5 *
        // __X__["__normal_cdf__K", self.iiv_cl] + __normal_cdf__K *
        // __X__["__normal_cdf__A5", self.iiv_cl] + __X__["__normal_cdf__A4",
        // self.iiv_cl]
        __X_72 = __0 * __ctx->ode->A[2] + __1 * __ctx->ode->A[2] +
                 __2 * __ctx->ode->A[3] + __3 * __ctx->ode->A[3] +
                 __normal_cdf__A5 * __X_66 + __normal_cdf__K * 0.0 +
                 __ctx->ode->A[2] * 0.0 + __ctx->ode->A[3] * 0.0 + 0.0;

        // __X__["__normal_cdf__K4", self.iiv_v] = __A__[self.cmt1, self.iiv_v]
        // * __0 + __A__[self.cmt1, self.iiv_v] * __1 + __A__[self.cmt1,
        // self.iiv_v] * __X__["__normal_cdf__A4", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_v] * __2 + __A__[self.cmt2, self.iiv_v] *
        // __3 + __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__A4",
        // __A__[self.cmt2]] + __normal_cdf__A5 * __X__["__normal_cdf__K",
        // self.iiv_v] + __normal_cdf__K * __X__["__normal_cdf__A5", self.iiv_v]
        // + __X__["__normal_cdf__A4", self.iiv_v]
        __X_73 = __0 * __ctx->ode->A[4] + __1 * __ctx->ode->A[4] +
                 __2 * __ctx->ode->A[5] + __3 * __ctx->ode->A[5] +
                 __normal_cdf__A5 * __X_67 + __normal_cdf__K * 0.0 +
                 __ctx->ode->A[4] * 0.0 + __ctx->ode->A[5] * 0.0 + 0.0;

        // __X__["__normal_cdf__K4", self.iiv_ka] = __A__[self.cmt1,
        // self.iiv_ka] * __0 + __A__[self.cmt1, self.iiv_ka] * __1 +
        // __A__[self.cmt1, self.iiv_ka] * __X__["__normal_cdf__A4",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] * __2 +
        // __A__[self.cmt2, self.iiv_ka] * __3 + __A__[self.cmt2, self.iiv_ka] *
        // __X__["__normal_cdf__A4", __A__[self.cmt2]] + __normal_cdf__A5 *
        // __X__["__normal_cdf__K", self.iiv_ka] + __normal_cdf__K *
        // __X__["__normal_cdf__A5", self.iiv_ka] + __X__["__normal_cdf__A4",
        // self.iiv_ka]
        __X_74 = __0 * __ctx->ode->A[6] + __1 * __ctx->ode->A[6] +
                 __2 * __ctx->ode->A[7] + __3 * __ctx->ode->A[7] +
                 __normal_cdf__A5 * __X_68 + __normal_cdf__K * 0.0 +
                 __ctx->ode->A[6] * 0.0 + __ctx->ode->A[7] * 0.0 + 0.0;

        // __X__["__normal_cdf__K4", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __0 + __A__[self.cmt1, self.eps_add] * __1 +
        // __A__[self.cmt1, self.eps_add] * __X__["__normal_cdf__A4",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.eps_add] * __2 +
        // __A__[self.cmt2, self.eps_add] * __3 + __A__[self.cmt2, self.eps_add]
        // * __X__["__normal_cdf__A4", __A__[self.cmt2]] + __normal_cdf__A5 *
        // __X__["__normal_cdf__K", self.eps_add] + __normal_cdf__K *
        // __X__["__normal_cdf__A5", self.eps_add] + __X__["__normal_cdf__A4",
        // self.eps_add]
        __X_75 = __0 * 0. + __1 * 0. + __2 * 0. + __3 * 0. +
                 __normal_cdf__A5 * __X_69 + __normal_cdf__K * 0.0 + 0. * 0.0 +
                 0. * 0.0 + 0.0;

        // __X__["__normal_cdf__K4", __A__[self.cmt1]] = __0 + __1 +
        // __X__["__normal_cdf__A4", __A__[self.cmt1]]
        __X_76 = __0 + __1 + 0.0;

        // __X__["__normal_cdf__K4", __A__[self.cmt2]] = __2 + __3 +
        // __X__["__normal_cdf__A4", __A__[self.cmt2]]
        __X_77 = __2 + __3 + 0.0;
      }

      // __normal_cdf__K3 = __normal_cdf__A3 + __normal_cdf__K *
      // __normal_cdf__K4
      __normal_cdf__K3 = __normal_cdf__A3 + __normal_cdf__K * __normal_cdf__K4;
      if (__ctx->first_order) {

        // __0 = __normal_cdf__K * __X__["__normal_cdf__K4", __A__[self.cmt1]]
        __0 = __normal_cdf__K * __X_76;

        // __1 = __normal_cdf__K4 * __X__["__normal_cdf__K", __A__[self.cmt1]]
        __1 = __normal_cdf__K4 * __X_70;

        // __2 = __normal_cdf__K * __X__["__normal_cdf__K4", __A__[self.cmt2]]
        __2 = __normal_cdf__K * __X_77;

        // __3 = __normal_cdf__K4 * __X__["__normal_cdf__K", __A__[self.cmt2]]
        __3 = __normal_cdf__K4 * __X_71;

        // __X__["__normal_cdf__K3", self.iiv_cl] = __A__[self.cmt1,
        // self.iiv_cl] * __0 + __A__[self.cmt1, self.iiv_cl] * __1 +
        // __A__[self.cmt1, self.iiv_cl] * __X__["__normal_cdf__A3",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] * __2 +
        // __A__[self.cmt2, self.iiv_cl] * __3 + __A__[self.cmt2, self.iiv_cl] *
        // __X__["__normal_cdf__A3", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K4", self.iiv_cl] + __normal_cdf__K4 *
        // __X__["__normal_cdf__K", self.iiv_cl] + __X__["__normal_cdf__A3",
        // self.iiv_cl]
        __X_78 = __0 * __ctx->ode->A[2] + __1 * __ctx->ode->A[2] +
                 __2 * __ctx->ode->A[3] + __3 * __ctx->ode->A[3] +
                 __normal_cdf__K * __X_72 + __normal_cdf__K4 * __X_66 +
                 __ctx->ode->A[2] * 0.0 + __ctx->ode->A[3] * 0.0 + 0.0;

        // __X__["__normal_cdf__K3", self.iiv_v] = __A__[self.cmt1, self.iiv_v]
        // * __0 + __A__[self.cmt1, self.iiv_v] * __1 + __A__[self.cmt1,
        // self.iiv_v] * __X__["__normal_cdf__A3", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_v] * __2 + __A__[self.cmt2, self.iiv_v] *
        // __3 + __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__A3",
        // __A__[self.cmt2]] + __normal_cdf__K * __X__["__normal_cdf__K4",
        // self.iiv_v] + __normal_cdf__K4 * __X__["__normal_cdf__K", self.iiv_v]
        // + __X__["__normal_cdf__A3", self.iiv_v]
        __X_79 = __0 * __ctx->ode->A[4] + __1 * __ctx->ode->A[4] +
                 __2 * __ctx->ode->A[5] + __3 * __ctx->ode->A[5] +
                 __normal_cdf__K * __X_73 + __normal_cdf__K4 * __X_67 +
                 __ctx->ode->A[4] * 0.0 + __ctx->ode->A[5] * 0.0 + 0.0;

        // __X__["__normal_cdf__K3", self.iiv_ka] = __A__[self.cmt1,
        // self.iiv_ka] * __0 + __A__[self.cmt1, self.iiv_ka] * __1 +
        // __A__[self.cmt1, self.iiv_ka] * __X__["__normal_cdf__A3",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] * __2 +
        // __A__[self.cmt2, self.iiv_ka] * __3 + __A__[self.cmt2, self.iiv_ka] *
        // __X__["__normal_cdf__A3", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K4", self.iiv_ka] + __normal_cdf__K4 *
        // __X__["__normal_cdf__K", self.iiv_ka] + __X__["__normal_cdf__A3",
        // self.iiv_ka]
        __X_80 = __0 * __ctx->ode->A[6] + __1 * __ctx->ode->A[6] +
                 __2 * __ctx->ode->A[7] + __3 * __ctx->ode->A[7] +
                 __normal_cdf__K * __X_74 + __normal_cdf__K4 * __X_68 +
                 __ctx->ode->A[6] * 0.0 + __ctx->ode->A[7] * 0.0 + 0.0;

        // __X__["__normal_cdf__K3", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __0 + __A__[self.cmt1, self.eps_add] * __1 +
        // __A__[self.cmt1, self.eps_add] * __X__["__normal_cdf__A3",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.eps_add] * __2 +
        // __A__[self.cmt2, self.eps_add] * __3 + __A__[self.cmt2, self.eps_add]
        // * __X__["__normal_cdf__A3", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K4", self.eps_add] + __normal_cdf__K4 *
        // __X__["__normal_cdf__K", self.eps_add] + __X__["__normal_cdf__A3",
        // self.eps_add]
        __X_81 = __0 * 0. + __1 * 0. + __2 * 0. + __3 * 0. +
                 __normal_cdf__K * __X_75 + __normal_cdf__K4 * __X_69 +
                 0. * 0.0 + 0. * 0.0 + 0.0;

        // __X__["__normal_cdf__K3", __A__[self.cmt1]] = __0 + __1 +
        // __X__["__normal_cdf__A3", __A__[self.cmt1]]
        __X_82 = __0 + __1 + 0.0;

        // __X__["__normal_cdf__K3", __A__[self.cmt2]] = __2 + __3 +
        // __X__["__normal_cdf__A3", __A__[self.cmt2]]
        __X_83 = __2 + __3 + 0.0;
      }

      // __normal_cdf__K2 = __normal_cdf__A2 + __normal_cdf__K *
      // __normal_cdf__K3
      __normal_cdf__K2 = __normal_cdf__A2 + __normal_cdf__K * __normal_cdf__K3;
      if (__ctx->first_order) {

        // __0 = __normal_cdf__K * __X__["__normal_cdf__K3", __A__[self.cmt1]]
        __0 = __normal_cdf__K * __X_82;

        // __1 = __normal_cdf__K3 * __X__["__normal_cdf__K", __A__[self.cmt1]]
        __1 = __normal_cdf__K3 * __X_70;

        // __2 = __normal_cdf__K * __X__["__normal_cdf__K3", __A__[self.cmt2]]
        __2 = __normal_cdf__K * __X_83;

        // __3 = __normal_cdf__K3 * __X__["__normal_cdf__K", __A__[self.cmt2]]
        __3 = __normal_cdf__K3 * __X_71;

        // __X__["__normal_cdf__K2", self.iiv_cl] = __A__[self.cmt1,
        // self.iiv_cl] * __0 + __A__[self.cmt1, self.iiv_cl] * __1 +
        // __A__[self.cmt1, self.iiv_cl] * __X__["__normal_cdf__A2",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] * __2 +
        // __A__[self.cmt2, self.iiv_cl] * __3 + __A__[self.cmt2, self.iiv_cl] *
        // __X__["__normal_cdf__A2", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K3", self.iiv_cl] + __normal_cdf__K3 *
        // __X__["__normal_cdf__K", self.iiv_cl] + __X__["__normal_cdf__A2",
        // self.iiv_cl]
        __X_84 = __0 * __ctx->ode->A[2] + __1 * __ctx->ode->A[2] +
                 __2 * __ctx->ode->A[3] + __3 * __ctx->ode->A[3] +
                 __normal_cdf__K * __X_78 + __normal_cdf__K3 * __X_66 +
                 __ctx->ode->A[2] * 0.0 + __ctx->ode->A[3] * 0.0 + 0.0;

        // __X__["__normal_cdf__K2", self.iiv_v] = __A__[self.cmt1, self.iiv_v]
        // * __0 + __A__[self.cmt1, self.iiv_v] * __1 + __A__[self.cmt1,
        // self.iiv_v] * __X__["__normal_cdf__A2", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_v] * __2 + __A__[self.cmt2, self.iiv_v] *
        // __3 + __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__A2",
        // __A__[self.cmt2]] + __normal_cdf__K * __X__["__normal_cdf__K3",
        // self.iiv_v] + __normal_cdf__K3 * __X__["__normal_cdf__K", self.iiv_v]
        // + __X__["__normal_cdf__A2", self.iiv_v]
        __X_85 = __0 * __ctx->ode->A[4] + __1 * __ctx->ode->A[4] +
                 __2 * __ctx->ode->A[5] + __3 * __ctx->ode->A[5] +
                 __normal_cdf__K * __X_79 + __normal_cdf__K3 * __X_67 +
                 __ctx->ode->A[4] * 0.0 + __ctx->ode->A[5] * 0.0 + 0.0;

        // __X__["__normal_cdf__K2", self.iiv_ka] = __A__[self.cmt1,
        // self.iiv_ka] * __0 + __A__[self.cmt1, self.iiv_ka] * __1 +
        // __A__[self.cmt1, self.iiv_ka] * __X__["__normal_cdf__A2",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] * __2 +
        // __A__[self.cmt2, self.iiv_ka] * __3 + __A__[self.cmt2, self.iiv_ka] *
        // __X__["__normal_cdf__A2", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K3", self.iiv_ka] + __normal_cdf__K3 *
        // __X__["__normal_cdf__K", self.iiv_ka] + __X__["__normal_cdf__A2",
        // self.iiv_ka]
        __X_86 = __0 * __ctx->ode->A[6] + __1 * __ctx->ode->A[6] +
                 __2 * __ctx->ode->A[7] + __3 * __ctx->ode->A[7] +
                 __normal_cdf__K * __X_80 + __normal_cdf__K3 * __X_68 +
                 __ctx->ode->A[6] * 0.0 + __ctx->ode->A[7] * 0.0 + 0.0;

        // __X__["__normal_cdf__K2", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __0 + __A__[self.cmt1, self.eps_add] * __1 +
        // __A__[self.cmt1, self.eps_add] * __X__["__normal_cdf__A2",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.eps_add] * __2 +
        // __A__[self.cmt2, self.eps_add] * __3 + __A__[self.cmt2, self.eps_add]
        // * __X__["__normal_cdf__A2", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K3", self.eps_add] + __normal_cdf__K3 *
        // __X__["__normal_cdf__K", self.eps_add] + __X__["__normal_cdf__A2",
        // self.eps_add]
        __X_87 = __0 * 0. + __1 * 0. + __2 * 0. + __3 * 0. +
                 __normal_cdf__K * __X_81 + __normal_cdf__K3 * __X_69 +
                 0. * 0.0 + 0. * 0.0 + 0.0;

        // __X__["__normal_cdf__K2", __A__[self.cmt1]] = __0 + __1 +
        // __X__["__normal_cdf__A2", __A__[self.cmt1]]
        __X_88 = __0 + __1 + 0.0;

        // __X__["__normal_cdf__K2", __A__[self.cmt2]] = __2 + __3 +
        // __X__["__normal_cdf__A2", __A__[self.cmt2]]
        __X_89 = __2 + __3 + 0.0;
      }

      // __normal_cdf__K1 = __normal_cdf__A1 + __normal_cdf__K *
      // __normal_cdf__K2
      __normal_cdf__K1 = __normal_cdf__A1 + __normal_cdf__K * __normal_cdf__K2;
      if (__ctx->first_order) {

        // __0 = __normal_cdf__K * __X__["__normal_cdf__K2", __A__[self.cmt1]]
        __0 = __normal_cdf__K * __X_88;

        // __1 = __normal_cdf__K2 * __X__["__normal_cdf__K", __A__[self.cmt1]]
        __1 = __normal_cdf__K2 * __X_70;

        // __2 = __normal_cdf__K * __X__["__normal_cdf__K2", __A__[self.cmt2]]
        __2 = __normal_cdf__K * __X_89;

        // __3 = __normal_cdf__K2 * __X__["__normal_cdf__K", __A__[self.cmt2]]
        __3 = __normal_cdf__K2 * __X_71;

        // __X__["__normal_cdf__K1", self.iiv_cl] = __A__[self.cmt1,
        // self.iiv_cl] * __0 + __A__[self.cmt1, self.iiv_cl] * __1 +
        // __A__[self.cmt1, self.iiv_cl] * __X__["__normal_cdf__A1",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] * __2 +
        // __A__[self.cmt2, self.iiv_cl] * __3 + __A__[self.cmt2, self.iiv_cl] *
        // __X__["__normal_cdf__A1", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K2", self.iiv_cl] + __normal_cdf__K2 *
        // __X__["__normal_cdf__K", self.iiv_cl] + __X__["__normal_cdf__A1",
        // self.iiv_cl]
        __X_90 = __0 * __ctx->ode->A[2] + __1 * __ctx->ode->A[2] +
                 __2 * __ctx->ode->A[3] + __3 * __ctx->ode->A[3] +
                 __normal_cdf__K * __X_84 + __normal_cdf__K2 * __X_66 +
                 __ctx->ode->A[2] * 0.0 + __ctx->ode->A[3] * 0.0 + 0.0;

        // __X__["__normal_cdf__K1", self.iiv_v] = __A__[self.cmt1, self.iiv_v]
        // * __0 + __A__[self.cmt1, self.iiv_v] * __1 + __A__[self.cmt1,
        // self.iiv_v] * __X__["__normal_cdf__A1", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_v] * __2 + __A__[self.cmt2, self.iiv_v] *
        // __3 + __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__A1",
        // __A__[self.cmt2]] + __normal_cdf__K * __X__["__normal_cdf__K2",
        // self.iiv_v] + __normal_cdf__K2 * __X__["__normal_cdf__K", self.iiv_v]
        // + __X__["__normal_cdf__A1", self.iiv_v]
        __X_91 = __0 * __ctx->ode->A[4] + __1 * __ctx->ode->A[4] +
                 __2 * __ctx->ode->A[5] + __3 * __ctx->ode->A[5] +
                 __normal_cdf__K * __X_85 + __normal_cdf__K2 * __X_67 +
                 __ctx->ode->A[4] * 0.0 + __ctx->ode->A[5] * 0.0 + 0.0;

        // __X__["__normal_cdf__K1", self.iiv_ka] = __A__[self.cmt1,
        // self.iiv_ka] * __0 + __A__[self.cmt1, self.iiv_ka] * __1 +
        // __A__[self.cmt1, self.iiv_ka] * __X__["__normal_cdf__A1",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] * __2 +
        // __A__[self.cmt2, self.iiv_ka] * __3 + __A__[self.cmt2, self.iiv_ka] *
        // __X__["__normal_cdf__A1", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K2", self.iiv_ka] + __normal_cdf__K2 *
        // __X__["__normal_cdf__K", self.iiv_ka] + __X__["__normal_cdf__A1",
        // self.iiv_ka]
        __X_92 = __0 * __ctx->ode->A[6] + __1 * __ctx->ode->A[6] +
                 __2 * __ctx->ode->A[7] + __3 * __ctx->ode->A[7] +
                 __normal_cdf__K * __X_86 + __normal_cdf__K2 * __X_68 +
                 __ctx->ode->A[6] * 0.0 + __ctx->ode->A[7] * 0.0 + 0.0;

        // __X__["__normal_cdf__K1", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __0 + __A__[self.cmt1, self.eps_add] * __1 +
        // __A__[self.cmt1, self.eps_add] * __X__["__normal_cdf__A1",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.eps_add] * __2 +
        // __A__[self.cmt2, self.eps_add] * __3 + __A__[self.cmt2, self.eps_add]
        // * __X__["__normal_cdf__A1", __A__[self.cmt2]] + __normal_cdf__K *
        // __X__["__normal_cdf__K2", self.eps_add] + __normal_cdf__K2 *
        // __X__["__normal_cdf__K", self.eps_add] + __X__["__normal_cdf__A1",
        // self.eps_add]
        __X_93 = __0 * 0. + __1 * 0. + __2 * 0. + __3 * 0. +
                 __normal_cdf__K * __X_87 + __normal_cdf__K2 * __X_69 +
                 0. * 0.0 + 0. * 0.0 + 0.0;

        // __X__["__normal_cdf__K1", __A__[self.cmt1]] = __0 + __1 +
        // __X__["__normal_cdf__A1", __A__[self.cmt1]]
        __X_94 = __0 + __1 + 0.0;

        // __X__["__normal_cdf__K1", __A__[self.cmt2]] = __2 + __3 +
        // __X__["__normal_cdf__A1", __A__[self.cmt2]]
        __X_95 = __2 + __3 + 0.0;
      }

      // __normal_cdf__cnd = __normal_cdf__RSQRT2PI * exp(-0.5 * __normal_cdf__x
      // * __normal_cdf__x) * (__normal_cdf__K * __normal_cdf__K1)
      __normal_cdf__cnd =
          __normal_cdf__K * __normal_cdf__K1 * __normal_cdf__RSQRT2PI *
          std::exp(-0.500000000000000 * std::pow(__normal_cdf__x, 2));
      if (__ctx->first_order) {

        // __0 = exp(-1 * 0.500000000000000 * __normal_cdf__x ** 2)
        __0 = std::exp(-0.500000000000000 * std::pow(__normal_cdf__x, 2));

        // __1 = __0 * __normal_cdf__K
        __1 = __0 * __normal_cdf__K;

        // __2 = __1 * __normal_cdf__K1
        __2 = __1 * __normal_cdf__K1;

        // __3 = __1 * __normal_cdf__RSQRT2PI
        __3 = __1 * __normal_cdf__RSQRT2PI;

        // __4 = __0 * __normal_cdf__K1 * __normal_cdf__RSQRT2PI
        __4 = __0 * __normal_cdf__K1 * __normal_cdf__RSQRT2PI;

        // __5 = __2 * __X__["__normal_cdf__RSQRT2PI", __A__[self.cmt1]]
        __5 = __2 * 0.0;

        // __6 = __3 * __X__["__normal_cdf__K1", __A__[self.cmt1]]
        __6 = __3 * __X_94;

        // __7 = __4 * __X__["__normal_cdf__K", __A__[self.cmt1]]
        __7 = __4 * __X_70;

        // __8 = __2 * __X__["__normal_cdf__RSQRT2PI", __A__[self.cmt2]]
        __8 = __2 * 0.0;

        // __9 = __3 * __X__["__normal_cdf__K1", __A__[self.cmt2]]
        __9 = __3 * __X_95;

        // __10 = __4 * __X__["__normal_cdf__K", __A__[self.cmt2]]
        __10 = __4 * __X_71;

        // __11 = 1.00000000000000 * __2 * __normal_cdf__RSQRT2PI *
        // __normal_cdf__x
        __11 =
            1.00000000000000 * __2 * __normal_cdf__RSQRT2PI * __normal_cdf__x;

        // __12 = __11 * __X__["__normal_cdf__x", __A__[self.cmt1]]
        __12 = __11 * __X_58;

        // __13 = __11 * __X__["__normal_cdf__x", __A__[self.cmt2]]
        __13 = __11 * __X_59;

        // __X__["__normal_cdf__cnd", self.iiv_cl] = -1 * __A__[self.cmt1,
        // self.iiv_cl] * __12 + __A__[self.cmt1, self.iiv_cl] * __5 +
        // __A__[self.cmt1, self.iiv_cl] * __6 + __A__[self.cmt1, self.iiv_cl] *
        // __7 + __A__[self.cmt2, self.iiv_cl] * __10 + -1 * __A__[self.cmt2,
        // self.iiv_cl] * __13 + __A__[self.cmt2, self.iiv_cl] * __8 +
        // __A__[self.cmt2, self.iiv_cl] * __9 + -1 * __11 *
        // __X__["__normal_cdf__x", self.iiv_cl] + __2 *
        // __X__["__normal_cdf__RSQRT2PI", self.iiv_cl] + __3 *
        // __X__["__normal_cdf__K1", self.iiv_cl] + __4 *
        // __X__["__normal_cdf__K", self.iiv_cl]
        __X_96 = __10 * __ctx->ode->A[3] + __2 * 0.0 + __3 * __X_90 +
                 __4 * __X_66 + __5 * __ctx->ode->A[2] +
                 __6 * __ctx->ode->A[2] + __7 * __ctx->ode->A[2] +
                 __8 * __ctx->ode->A[3] + __9 * __ctx->ode->A[3] +
                 -1 * __11 * __X_54 + -1 * __12 * __ctx->ode->A[2] +
                 -1 * __13 * __ctx->ode->A[3];

        // __X__["__normal_cdf__cnd", self.iiv_v] = -1 * __A__[self.cmt1,
        // self.iiv_v] * __12 + __A__[self.cmt1, self.iiv_v] * __5 +
        // __A__[self.cmt1, self.iiv_v] * __6 + __A__[self.cmt1, self.iiv_v] *
        // __7 + __A__[self.cmt2, self.iiv_v] * __10 + -1 * __A__[self.cmt2,
        // self.iiv_v] * __13 + __A__[self.cmt2, self.iiv_v] * __8 +
        // __A__[self.cmt2, self.iiv_v] * __9 + -1 * __11 *
        // __X__["__normal_cdf__x", self.iiv_v] + __2 *
        // __X__["__normal_cdf__RSQRT2PI", self.iiv_v] + __3 *
        // __X__["__normal_cdf__K1", self.iiv_v] + __4 *
        // __X__["__normal_cdf__K", self.iiv_v]
        __X_97 = __10 * __ctx->ode->A[5] + __2 * 0.0 + __3 * __X_91 +
                 __4 * __X_67 + __5 * __ctx->ode->A[4] +
                 __6 * __ctx->ode->A[4] + __7 * __ctx->ode->A[4] +
                 __8 * __ctx->ode->A[5] + __9 * __ctx->ode->A[5] +
                 -1 * __11 * __X_55 + -1 * __12 * __ctx->ode->A[4] +
                 -1 * __13 * __ctx->ode->A[5];

        // __X__["__normal_cdf__cnd", self.iiv_ka] = -1 * __A__[self.cmt1,
        // self.iiv_ka] * __12 + __A__[self.cmt1, self.iiv_ka] * __5 +
        // __A__[self.cmt1, self.iiv_ka] * __6 + __A__[self.cmt1, self.iiv_ka] *
        // __7 + __A__[self.cmt2, self.iiv_ka] * __10 + -1 * __A__[self.cmt2,
        // self.iiv_ka] * __13 + __A__[self.cmt2, self.iiv_ka] * __8 +
        // __A__[self.cmt2, self.iiv_ka] * __9 + -1 * __11 *
        // __X__["__normal_cdf__x", self.iiv_ka] + __2 *
        // __X__["__normal_cdf__RSQRT2PI", self.iiv_ka] + __3 *
        // __X__["__normal_cdf__K1", self.iiv_ka] + __4 *
        // __X__["__normal_cdf__K", self.iiv_ka]
        __X_98 = __10 * __ctx->ode->A[7] + __2 * 0.0 + __3 * __X_92 +
                 __4 * __X_68 + __5 * __ctx->ode->A[6] +
                 __6 * __ctx->ode->A[6] + __7 * __ctx->ode->A[6] +
                 __8 * __ctx->ode->A[7] + __9 * __ctx->ode->A[7] +
                 -1 * __11 * __X_56 + -1 * __12 * __ctx->ode->A[6] +
                 -1 * __13 * __ctx->ode->A[7];

        // __X__["__normal_cdf__cnd", self.eps_add] = -1 * __A__[self.cmt1,
        // self.eps_add] * __12 + __A__[self.cmt1, self.eps_add] * __5 +
        // __A__[self.cmt1, self.eps_add] * __6 + __A__[self.cmt1, self.eps_add]
        // * __7 + __A__[self.cmt2, self.eps_add] * __10 + -1 * __A__[self.cmt2,
        // self.eps_add] * __13 + __A__[self.cmt2, self.eps_add] * __8 +
        // __A__[self.cmt2, self.eps_add] * __9 + -1 * __11 *
        // __X__["__normal_cdf__x", self.eps_add] + __2 *
        // __X__["__normal_cdf__RSQRT2PI", self.eps_add] + __3 *
        // __X__["__normal_cdf__K1", self.eps_add] + __4 *
        // __X__["__normal_cdf__K", self.eps_add]
        __X_99 = __10 * 0. + __2 * 0.0 + __3 * __X_93 + __4 * __X_69 +
                 __5 * 0. + __6 * 0. + __7 * 0. + __8 * 0. + __9 * 0. +
                 -1 * __11 * __X_57 + -1 * __12 * 0. + -1 * __13 * 0.;

        // __X__["__normal_cdf__cnd", __A__[self.cmt1]] = -1 * __12 + __5 + __6
        // + __7
        __X_100 = __5 + __6 + __7 + -1 * __12;

        // __X__["__normal_cdf__cnd", __A__[self.cmt2]] = __10 + -1 * __13 + __8
        // + __9
        __X_101 = __10 + __8 + __9 + -1 * __13;
      }
      if (__normal_cdf__x > 0) {

        // __normal_cdf__cnd = 1 - __normal_cdf__cnd
        __normal_cdf__cnd = 1 + -1 * __normal_cdf__cnd;
        if (__ctx->first_order) {

          // __X__["__normal_cdf__cnd", self.iiv_cl] = -1 * __A__[self.cmt1,
          // self.iiv_cl] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.iiv_cl] * __X__["__normal_cdf__cnd",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__cnd", self.iiv_cl]
          __X_96 = -1 * __X_96 + -1 * __ctx->ode->A[2] * __X_100 +
                   -1 * __ctx->ode->A[3] * __X_101;

          // __X__["__normal_cdf__cnd", self.iiv_v] = -1 * __A__[self.cmt1,
          // self.iiv_v] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__cnd",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__cnd", self.iiv_v]
          __X_97 = -1 * __X_97 + -1 * __ctx->ode->A[4] * __X_100 +
                   -1 * __ctx->ode->A[5] * __X_101;

          // __X__["__normal_cdf__cnd", self.iiv_ka] = -1 * __A__[self.cmt1,
          // self.iiv_ka] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.iiv_ka] * __X__["__normal_cdf__cnd",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__cnd", self.iiv_ka]
          __X_98 = -1 * __X_98 + -1 * __ctx->ode->A[6] * __X_100 +
                   -1 * __ctx->ode->A[7] * __X_101;

          // __X__["__normal_cdf__cnd", self.eps_add] = -1 * __A__[self.cmt1,
          // self.eps_add] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] + -1 *
          // __A__[self.cmt2, self.eps_add] * __X__["__normal_cdf__cnd",
          // __A__[self.cmt2]] + -1 * __X__["__normal_cdf__cnd", self.eps_add]
          __X_99 = -1 * __X_99 + -1 * 0. * __X_100 + -1 * 0. * __X_101;

          // __X__["__normal_cdf__cnd", __A__[self.cmt1]] = -1 *
          // __X__["__normal_cdf__cnd", __A__[self.cmt1]]
          __X_100 = -1 * __X_100;

          // __X__["__normal_cdf__cnd", __A__[self.cmt2]] = -1 *
          // __X__["__normal_cdf__cnd", __A__[self.cmt2]]
          __X_101 = -1 * __X_101;
        }
      }

      // __normal_cdf__return = __normal_cdf__cnd
      __normal_cdf__return = __normal_cdf__cnd;
      if (__ctx->first_order) {

        // __X__["__normal_cdf__return", self.iiv_cl] = __A__[self.cmt1,
        // self.iiv_cl] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_cl] * __X__["__normal_cdf__cnd",
        // __A__[self.cmt2]] + __X__["__normal_cdf__cnd", self.iiv_cl]
        __X_102 =
            __ctx->ode->A[2] * __X_100 + __ctx->ode->A[3] * __X_101 + __X_96;

        // __X__["__normal_cdf__return", self.iiv_v] = __A__[self.cmt1,
        // self.iiv_v] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_v] * __X__["__normal_cdf__cnd",
        // __A__[self.cmt2]] + __X__["__normal_cdf__cnd", self.iiv_v]
        __X_103 =
            __ctx->ode->A[4] * __X_100 + __ctx->ode->A[5] * __X_101 + __X_97;

        // __X__["__normal_cdf__return", self.iiv_ka] = __A__[self.cmt1,
        // self.iiv_ka] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.iiv_ka] * __X__["__normal_cdf__cnd",
        // __A__[self.cmt2]] + __X__["__normal_cdf__cnd", self.iiv_ka]
        __X_104 =
            __ctx->ode->A[6] * __X_100 + __ctx->ode->A[7] * __X_101 + __X_98;

        // __X__["__normal_cdf__return", self.eps_add] = __A__[self.cmt1,
        // self.eps_add] * __X__["__normal_cdf__cnd", __A__[self.cmt1]] +
        // __A__[self.cmt2, self.eps_add] * __X__["__normal_cdf__cnd",
        // __A__[self.cmt2]] + __X__["__normal_cdf__cnd", self.eps_add]
        __X_105 = 0. * __X_100 + 0. * __X_101 + __X_99;

        // __X__["__normal_cdf__return", __A__[self.cmt1]] =
        // __X__["__normal_cdf__cnd", __A__[self.cmt1]]
        __X_106 = __X_100;

        // __X__["__normal_cdf__return", __A__[self.cmt2]] =
        // __X__["__normal_cdf__cnd", __A__[self.cmt2]]
        __X_107 = __X_101;
      }

      // CUM = __normal_cdf__return
      CUM = __normal_cdf__return;
      if (__ctx->first_order) {

        // __X__["CUM", self.iiv_cl] = __A__[self.cmt1, self.iiv_cl] *
        // __X__["__normal_cdf__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.iiv_cl] * __X__["__normal_cdf__return", __A__[self.cmt2]] +
        // __X__["__normal_cdf__return", self.iiv_cl]
        __X_108 =
            __ctx->ode->A[2] * __X_106 + __ctx->ode->A[3] * __X_107 + __X_102;

        // __X__["CUM", self.iiv_v] = __A__[self.cmt1, self.iiv_v] *
        // __X__["__normal_cdf__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.iiv_v] * __X__["__normal_cdf__return", __A__[self.cmt2]] +
        // __X__["__normal_cdf__return", self.iiv_v]
        __X_109 =
            __ctx->ode->A[4] * __X_106 + __ctx->ode->A[5] * __X_107 + __X_103;

        // __X__["CUM", self.iiv_ka] = __A__[self.cmt1, self.iiv_ka] *
        // __X__["__normal_cdf__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.iiv_ka] * __X__["__normal_cdf__return", __A__[self.cmt2]] +
        // __X__["__normal_cdf__return", self.iiv_ka]
        __X_110 =
            __ctx->ode->A[6] * __X_106 + __ctx->ode->A[7] * __X_107 + __X_104;

        // __X__["CUM", self.eps_add] = __A__[self.cmt1, self.eps_add] *
        // __X__["__normal_cdf__return", __A__[self.cmt1]] + __A__[self.cmt2,
        // self.eps_add] * __X__["__normal_cdf__return", __A__[self.cmt2]] +
        // __X__["__normal_cdf__return", self.eps_add]
        __X_111 = 0. * __X_106 + 0. * __X_107 + __X_105;

        // __X__["CUM", __A__[self.cmt1]] = __X__["__normal_cdf__return",
        // __A__[self.cmt1]]
        __X_112 = __X_106;

        // __X__["CUM", __A__[self.cmt2]] = __X__["__normal_cdf__return",
        // __A__[self.cmt2]]
        __X_113 = __X_107;
      }

      // __Y__["type"] = 1
      __ctx->Ytype = 1;

      // __Y__[:] = CUM
      __ctx->Y[0] = CUM;
      if (__ctx->first_order) {

        // __Y__[self.iiv_cl] = __A__[self.cmt1, self.iiv_cl] * __X__["CUM",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] * __X__["CUM",
        // __A__[self.cmt2]] + __X__["CUM", self.iiv_cl]
        __ctx->Y[1] =
            __ctx->ode->A[2] * __X_112 + __ctx->ode->A[3] * __X_113 + __X_108;

        // __Y__[self.iiv_v] = __A__[self.cmt1, self.iiv_v] * __X__["CUM",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_v] * __X__["CUM",
        // __A__[self.cmt2]] + __X__["CUM", self.iiv_v]
        __ctx->Y[2] =
            __ctx->ode->A[4] * __X_112 + __ctx->ode->A[5] * __X_113 + __X_109;

        // __Y__[self.iiv_ka] = __A__[self.cmt1, self.iiv_ka] * __X__["CUM",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] * __X__["CUM",
        // __A__[self.cmt2]] + __X__["CUM", self.iiv_ka]
        __ctx->Y[3] =
            __ctx->ode->A[6] * __X_112 + __ctx->ode->A[7] * __X_113 + __X_110;

        // __Y__[self.eps_add] = __A__[self.cmt1, self.eps_add] * __X__["CUM",
        // __A__[self.cmt1]] + __A__[self.cmt2, self.eps_add] * __X__["CUM",
        // __A__[self.cmt2]] + __X__["CUM", self.eps_add]
        __ctx->Y[4] = 0. * __X_112 + 0. * __X_113 + __X_111;

        // __Y__[__A__[self.cmt1]] = __X__["CUM", __A__[self.cmt1]]

        // __Y__[__A__[self.cmt2]] = __X__["CUM", __A__[self.cmt2]]
      }

      // return
      goto __return;
    }

    // __Y__["type"] = 0
    __ctx->Ytype = 0;

    // __Y__[:] = self.eps_add + IPRED
    __ctx->Y[0] = IPRED + __self_eps_add;
    if (__ctx->first_order) {

      // __Y__[self.iiv_cl] = __A__[self.cmt1, self.iiv_cl] * __X__["IPRED",
      // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_cl] * __X__["IPRED",
      // __A__[self.cmt2]] + __X__["IPRED", self.iiv_cl]
      __ctx->Y[1] =
          __ctx->ode->A[2] * __X_28 + __ctx->ode->A[3] * __X_29 + __X_24;

      // __Y__[self.iiv_v] = __A__[self.cmt1, self.iiv_v] * __X__["IPRED",
      // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_v] * __X__["IPRED",
      // __A__[self.cmt2]] + __X__["IPRED", self.iiv_v]
      __ctx->Y[2] =
          __ctx->ode->A[4] * __X_28 + __ctx->ode->A[5] * __X_29 + __X_25;

      // __Y__[self.iiv_ka] = __A__[self.cmt1, self.iiv_ka] * __X__["IPRED",
      // __A__[self.cmt1]] + __A__[self.cmt2, self.iiv_ka] * __X__["IPRED",
      // __A__[self.cmt2]] + __X__["IPRED", self.iiv_ka]
      __ctx->Y[3] =
          __ctx->ode->A[6] * __X_28 + __ctx->ode->A[7] * __X_29 + __X_26;

      // __Y__[self.eps_add] = __A__[self.cmt1, self.eps_add] * __X__["IPRED",
      // __A__[self.cmt1]] + __A__[self.cmt2, self.eps_add] * __X__["IPRED",
      // __A__[self.cmt2]] + __X__["IPRED", self.eps_add] + 1
      __ctx->Y[4] = 1 + 0. * __X_28 + 0. * __X_29 + __X_27;

      // __Y__[__A__[self.cmt1]] = __X__["IPRED", __A__[self.cmt1]]

      // __Y__[__A__[self.cmt2]] = __X__["IPRED", __A__[self.cmt2]]
    }

    // return
    goto __return;
  // #endregion

  // #region Return
  __return : {
    if (__locals != nullptr) {
      (*__locals->dlocals)["cl"] = cl;
      (*__locals->dlocals)["v"] = v;
      (*__locals->dlocals)["ka"] = ka;
      (*__locals->dlocals)["k"] = k;
      (*__locals->dlocals)["IPRED"] = IPRED;
    }
    return Ok();
  }
    // #endregion
  }
};

__DYLIB_EXPORT IModule *__dylib_module_factory() { return new __Module(); }
